from psd_tools import PSDImage
import re, sys, os

filelocation = os.getcwd()+'/'+sys.argv[1]
path = os.path.dirname(os.path.realpath(__file__))
print(path)

# psd = PSDImage.load('my_image.psd')
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
      print(layer.bbox)
      # create css
      def namelayer(checkname, i):
        if(checkname in elements):
          i += 1
          # remove _n if int higher than 1
          if(i>1):
            splitstring = checkname.split('_')
            checkname = ''.join(splitstring.pop())
          return namelayer(checkname+"_"+str(i), i)
        else:
          return checkname

      name = namelayer(layer.name, 0)
      elements.append(name)
      name = re.sub(',','', name)
      name = re.sub('\.','', name)
      name = re.sub('\s', '-', name)
      css += '#'+name+'{\n  left: ' + str(layer.bbox[0]) + 'px;\n'
      css += '  position: absolute;\n'
      css += '  top: ' + str(layer.bbox[1]) + 'px;\n'
      css += '  width: ' + str(layer.bbox[2] - layer.bbox[0]) + 'px;\n'
      css += '  height: ' + str(layer.bbox[3] - layer.bbox[1]) + 'px;\n'
      css += '  background-image: url("' + name + '.png");\n'
      css += '}\n'

      # create html
      html += '  <div id="' + name + '"></div>\n'

      # save images as images
      layer_image = layer.as_PIL()
      layer_image.save(path+'/bin/' + name + '.png')

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
