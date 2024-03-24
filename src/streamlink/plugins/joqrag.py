"""
$description Japanese Internet visual radio "Super! A&G+" (f.k.a. AGQR) operated by Nippon Cultural Broadcasting (JOQR).
$url www.uniqueradio.jp/agplayer5
$url joqr.co.jp
$type live
$metadata author
$metadata title
"""

import re
from urllib.parse import unquote_plus, urljoin

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream


@pluginmatcher(re.compile(r"https?://www\.uniqueradio\.jp/agplayer5/(?:player\.php|inc-player-hls\.php)"))
@pluginmatcher(re.compile(r"https?://(?:www\.)?joqr\.co\.jp/(?:ag|qr/(?:agdailyprogram|agregularprogram))"))
class JoqrAg(Plugin):
    _URL_HOST = "https://www.uniqueradio.jp"
    _URL_METADATA = f"{_URL_HOST}/aandg"
    _URL_PLAYER = f"{_URL_HOST}/agplayer5/inc-player-hls.php"

    def _get_streams(self):
        self.id = "live"
        self.author = "超!A&G+"

        self.title = self.session.http.get(
            self._URL_METADATA,
            schema=validate.Schema(
                re.compile(r"""var\s+Program_name\s*=\s*("|')(?P<name>(?:(?!\1).)+)\1"""),
                validate.none_or_all(
                    validate.get("name"),
                    validate.transform(unquote_plus),
                ),
            ),
        )
        if self.title == "放送休止":
            return None

        m3u8_url = self.session.http.get(
            self._URL_PLAYER,
            schema=validate.Schema(
                validate.parse_html(),
                validate.xml_xpath_string(".//video[@id='my-video']/source[@type='application/x-mpegURL']/@src"),
                validate.none_or_all(
                    validate.transform(lambda m3u8_path: urljoin(self._URL_HOST, m3u8_path)),
                ),
            ),
        )
        if not m3u8_url:
            return None

        return HLSStream.parse_variant_playlist(self.session, m3u8_url)


__plugin__ = JoqrAg