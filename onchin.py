#!/usr/bin/env python3
from html import escape
from os.path import basename
from urllib.parse import quote
import os
import sys

play_next = False  # play next file after the current one ends
playable_exts = (".mp3", ".ogg")
cover_names = ("cover", "folder")
image_exts = ("jpg", "png", "jpeg")
covers = tuple("{}.{}".format(name, ext) for name in cover_names for ext in image_exts)

# not checked for injections etc
css = """
body {
	font-family: monospace;
	background-color: #2d2d2d;
}

a {
	font-size: 13px;
	color: #777777;
	text-decoration: none;
}

audio#player {
	margin-top: 10px;
	display: flex;
	width: 500px;
}

img#cover {
	display: flex;
	max-height: 500px;
	max-width: 500px;
}

#nani {
	margin: 40px;
	display: flex;
}

#np {
	font-size: 15px;
	color: #ffffff;
	padding-top: 10px;
	text-align: center;
	max-width: 500px;
}

#song {
	font-size: 14px;
	line-height: 20px;
	color: #cbcbcb;
}
"""

js = """
function basename(path) {
	const elems = path.split('/');
	return elems[elems.length - 1];
}

function playFile(path) {
	np.innerText = basename(decodeURIComponent(path));
	player.src = path;
	player.play();
	return false;
}

function main() {
	const files = Array.map(document.querySelectorAll("#files a[data-file]"), (a) => a.dataset.file);
	const playNext = %s;

	if(playNext)
		player.addEventListener("ended", () => {
			let i = files.indexOf(basename(player.src));
			if(i + 1 < files.length)
				playFile(files[i+1]);
		});
}
""" % ("true" if play_next else "false")

reindent = lambda text, times=1: ''.join(("\t" * times) + x + "\n" for x in text.split("\n"))
rjs = reindent(js, 2)
rcss = reindent(css, 2)


class Entry:
	def __init__(self, name):
		self.name = name
		self.playable = False


def gendir(path):
	files = [Entry("..")]
	regular = []
	playable = []
	cover = ""
	path = os.path.realpath(path)

	for entry in sorted(os.listdir(path)):
		files.append(Entry(entry))
		i = len(files) - 1
		l = entry.lower()

		if os.path.isdir(entry):
			continue

		if l.endswith(playable_exts):
			files[i].playable = True

		if l in covers:
			cover = entry

	html = "<!doctype html>\n"
	html += "<html>\n<head>\n"
	html += "	<title>{}</title>\n".format(escape(basename(path)))
	html += '	<meta charset="utf-8" />\n'
	html += "	<style>{}</style>\n".format(rcss)
	html += "	<script>{}</script>\n".format(rjs)
	html += "</head>\n"
	html += '<body onload="main()">\n'
	html += '<div id="nani"><div id="dupa">\n'
	if cover:
		html += '	<img id="cover" src="{}" />\n'.format(cover)
	html += '		<audio id="player" controls></audio>\n'
	html += '		<div id="np"></div>\n'
	html += "	</div>\n"
	html += '	<ul id="files">\n'
	for f in files:
		html += "	<li><a "
		if f.playable:
			html += 'id="song" href="{f}" data-file="{f}" onclick="return playFile(this.dataset.file)"'.format(f=quote(f.name))
		else:
			html += 'href="{}"'.format(quote(f.name))
		html += ">{}</a></li>\n".format(escape(f.name))
	html += "</ul>\n</div>\n</body>\n</html>\n"
	return html

if __name__ == "__main__":
	print(gendir(sys.argv[1]))
