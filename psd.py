from psd_tools import PSDImage
import re, sys, os, argparse

parser = argparse.ArgumentParser(description="A script that converts a Photoshop file into HTML/CSS Edit")
parser.add_argument("-f", "--file", required=True)
# parser.add_argument("-d", "--dynamic", action='store_true')
args, leftovers = parser.parse_known_args()

filelocation = os.getcwd()+'/'+args.file
path = os.path.dirname(os.path.realpath(__file__))

psd = PSDImage.load(filelocation)

elements = []

def layerstoimage(layers):
  global elements
  html, css = '', ''
  for layer in reversed(layers):
    if hasattr(layer, 'layers'):
      site = layerstoimage(layer.layers)
      html += site[0]
      css += site[1]
    else:
      # if layer name is already used for an id append _n, where n is smallest availible number
      def namelayer(checkname, i):
        if(checkname in elements):
          i += 1
          # remove _n if i higher than 1
          if(i>1):
            splitstring = checkname.split('_')
            splitstring.pop()
            checkname = ''.join(splitstring)
          return namelayer(checkname+"_"+str(i), i)
        else:
          return checkname

      # process name to make unique and strip special characters
      name = namelayer(layer.name, 0)
      elements.append(name)
      name = re.sub(',','', name)
      name = re.sub('\.','', name)
      name = re.sub('\s', '-', name)
      name = re.sub('\*', '-', name)
      name = re.sub('©', '', name)
      print("Processing Layer: " + name)

      # get width
      width = layer.bbox[2] - layer.bbox[0]
      #  if(args.dynamic):
      #    width = psd.header.width/width
      #    width = str(width) + '%'
      #  else:
      #    width = str(width) + 'px'
      width = str(width) + 'px'

      # create css
      css += '#'+name+'{\n  left: ' + str(layer.bbox[0]) + 'px;\n'
      css += '  position: absolute;\n'
      css += '  top: ' + str(layer.bbox[1]) + 'px;\n'
      css += '  width: ' + width + ';\n'
      css += '  height: ' + str(layer.bbox[3] - layer.bbox[1]) + 'px;\n'
      css += '  background-image: url("images/' + name + '.png");\n'
      css += '}\n'

      # create html
      html += '  <div id="' + name + '"></div>\n'

      # save images as images
      layer_image = layer.as_PIL()
      layer_image.save(path+'/bin/images/' + name + '.png')

  return html, css

html = '<html>\n<head>\n  <link rel="stylesheet" href="index.css">\n</head>\n<body>\n'
css = ''

site = layerstoimage(psd.layers)
html += site[0]
html += '</body>\n</html>'
css += site[1]

f = open(path+'/bin/index.html','w')
f.write(html)
f.close()

f = open(path+'/bin/index.css','w')
f.write(css)
f.close()
