#!/usr/bin/python

import argparse
import os
import re
import urllib
import base64

import cssutils
import cssutils.css

### Parse args

cliParser = argparse.ArgumentParser(
  description="CSSDownload - Download external CSS resources")

cliParser.add_argument('-f', 
                       '--force', 
                      help="Overwrite without prompting.", 
                      action='store_true')
cliParser.add_argument('--baseurl', help="Base URL")
cliParser.add_argument('infile', help="Input file names", nargs='+')
cliParser.add_argument('outdir', help="Output directory")

args = cliParser.parse_args()

### Process

fetched = []

for inFile in args.infile:
  inCss = cssutils.parseFile(inFile)
  for rule in inCss.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
    for prop in rule.style:
      if prop.name in ['background', 'background-image']:
        matches = re.search(r"url\(([^)]+)\)", prop.value)
        if matches:
          url = matches.group(1)
          if url in fetched:
            continue
          fetched.append(url)

          parsedUrl = urllib.parse.urlparse(url)


          if parsedUrl.scheme == 'data':
            print("Data url encountered, selector='" 
                  + prop.selectorText + "'")
            filename = input('Enter a filename for the dataurl resource: ')
            if not filename:
              print('No filename provided.')
              print('Continuing.')
              continue

              matches = re.search(r"base64,(.*)", parsedUrl.path)
              if matches:
                data = base64.b64decode(matches.group(1))
                path = os.path.join(args.outdir, filename)
                if os.path.exists(path) and not args.force:
                  print ('File ' + path + ' already exists.')
                  answer = input('Overwrite? [y/N]: ')
                  if answer.strip() != 'y':
                    print ('Nothing done.')
                    print ('Continuing.')
                    continue
                with open(path, 'w') as file:
                  file.write(data)
              else:
                print("Not base64 data url.")
                print("Continuing.")
                continue
          else:
            if not parsedUrl.scheme:
              url = urllib.parse.urljoin(args.baseurl, url)
            filename = os.path.basename(parsedUrl.path)
            path = os.path.join(args.outdir, filename)
            if os.path.exists(path) and not args.force:
              print ('File ' + path + ' already exists.')
              answer = input('Overwrite? [y/N]: ')
              if answer.strip() != 'y':
                print ('Nothing done.')
                print ('Continuing.')
                continue
            try:
              urllib.request.urlretrieve(url, path)
            except urllib.error.HTTPError as e:
              print('HTTP error ' + str(e.code))
              print('Continuing.')

