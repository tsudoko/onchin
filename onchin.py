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
	margin: 40px;
}

a {
	font-size: 13px;
	color: #777;
	text-decoration: none;
}

#container, #files {
	display: inline-block;
	vertical-align: top;
}

audio#player {
	display: flex;
	margin-top: 10px;
	width: 500px;
}

img#cover {
	display: flex;
	max-height: 500px;
	max-width: 500px;
}

#np {
	font-size: 15px;
	padding-top: 10px;
	text-align: center;
	color: #fff;
	max-width: 500px;
}

a[data-playable] {
	font-size: 14px;
	line-height: 20px;
	color: #cbcbcb;
}

ul {
	padding-left: 2em;
}

ul li {
	list-style-type: none;
}

ul li:before {
	content: "> ";
}

ul li[data-np]:before {
	content: "> ";
	color: #454545;
}
"""

js = """
function basename(path) {
	const elems = path.split('/');
	return elems[elems.length - 1];
}

function play(a) {
	const path = a.href;
	const prev = document.querySelector(`#files a[href="${basename(player.src)}"]`);
	console.log(`#files a[href="${basename(player.src)}"]`);
	console.log(prev);

	if(prev)
		prev.parentNode.removeAttribute("data-np");

	a.parentNode.dataset.np = true;
	np.innerText = basename(decodeURIComponent(path));
	player.src = path;
	player.play();
	return false;
}

function main() {
	const fileNodes = document.querySelectorAll("#files a[data-playable]");
	const files = Array.map(fileNodes, (a) => a.href);
	const playNext = %s;

	fileNodes.forEach((a) => a.onclick = () => play(a));

	if(playNext)
		player.addEventListener("ended", () => {
			let i = files.indexOf(player.src);
			if(i + 1 < files.length)
				play(fileNodes[i+1]);
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
	html += '	<div id="container">\n'
	if cover:
		html += '		<img id="cover" src="{}" />\n'.format(cover)
	html += '		<audio id="player" controls></audio>\n'
	html += '		<div id="np"></div>\n'
	html += "	</div>\n"
	html += '	<ul id="files">\n'
	for f in files:
		html += '	<li><a href="{}"'.format(quote(f.name))
		if f.playable:
			html += " data-playable"
		html += ">{}</a></li>\n".format(escape(f.name))
	html += "</ul>\n</body>\n</html>\n"
	return html

if __name__ == "__main__":
	print(gendir(sys.argv[1]))
