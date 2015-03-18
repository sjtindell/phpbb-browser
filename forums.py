import sys
import requests
from bs4 import BeautifulSoup


usage = '''usage:
forums <-> topics <-> posts
press the # of the forum/topic to browse to it
press b to back out to the previous level
press q to quit
modify forums.py to add keys'''

index_dict = {'cabrillo': 'http://oslab.cishawks.net/forum/index.php',
			  'adblock': 'https://adblockplus.org/forum/',
			  'asterisk': 'http://forums.asterisk.org/'}


if sys.argv[1] in index_dict.keys():
	index = index_dict[sys.argv[1]]
else:
	index = sys.argv[1]

# {forum name: link}
# {forum name: [(topictitle, link), ...]}
# {topics links: [(name, post), ...]}
# lists of tuples to keep order

forums = { }
topics = { }
posts_dict = { }


# Part 0
# initital scrape of forums page
# {forum name: link}
def get_forums():
  response = requests.get(index)
  soup = BeautifulSoup(response.text, 'html5lib')
  
  for anchor in soup.find_all('a'):
    try:
      if anchor['class'] == ['forumtitle']:
        # if few entries, more readable menu
        if 'Archive' not in anchor.text:
	  forums[anchor.text] = index + anchor['href'][2:]
    except KeyError:  
      pass

# {forum name: [(topictitle, link), ...]}
def browse_forum(forum):
  url = forums[forum]
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html5lib')
  topics_list = []
  
  for anchor in soup.find_all('a'):
    try:
      if anchor['class'] == ['topictitle']:
        topics_list.append((anchor.text, 
                            index + anchor['href'][2:]))
    except KeyError:
      pass
  
  topics[forum] = topics_list

# {topics links: [(name, post), ...]}
def browse_topic(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html5lib')
  names, posts = [], []
  
  for tag in soup.find_all('p'):
    if 'class' in tag.attrs.keys() and tag['class'] == ['author']:
        for anchor in tag.find_all('a'):
          names.append(anchor.text)
  for div in soup.find_all('div'):
    if 'class' in div.attrs.keys() and div['class'] == ['content']:
        posts.append(div.text)
  
  matched = zip([item for item in names  if item != ''], posts)
  posts_dict[url] = [(k, v) for k, v in matched]


# Part 1
# tmp dicts for user to
# access indexed links
def show_index():
  tmp = {}
  i = 0
  
  for key in forums.keys():
    i += 1
    print i, key
    tmp[i] = key
  return tmp  

def get_topics(forum):
  tmp = {}
  i = 0
  
  for key, lst in topics.items():
    if forum == key:
      for topic in lst:
        i += 1
        tmp[i] = topic[0]
        print i, topic[0]
  return tmp

def show_posts(url):
  for pair in posts_dict[url]:
    print '-' * 10
    print pair[0]
    # extra print, whitespace
    print; print pair[1]
    

# Part 2
def read_forums():
  while True:
    # show entries while adding to dict
    # for user access by num
    index = show_index()
    x = raw_input('#> ')
    
    if x == 'q':
      sys.exit(0)
    # unaddressed dict entry
    elif x == 'b':
      print 'q to quit'
    else:
      forum = index[int(x)]
      if forum in topics.keys():
        return forum
      else:
        print 'browsing...'
        browse_forum(forum)
        return forum

def read_topics(forum):
  # topics, {topic: link}
  while True:
    all_topics = get_topics(forum)
    y = raw_input('#> ')
    
    if y == 'q':
      sys.exit(0)
    elif y == 'b':
      break
    else:
      for lst in topics[forum]:
        if all_topics[int(y)] == lst[0]:
          if lst[1] not in posts_dict.keys():
            print 'browsing...'
            browse_topic(lst[1])
            show_posts(lst[1])
            y = raw_input('> '); print
            if y == 'b':
              break
          else:
            show_posts(lst[1])
            y = raw_input('> '); print
            if y == 'b':
              break
     

# Part 3
def main():
  print usage; print 
  get_forums()
  while True:
    v = read_forums()
    read_topics(v)

main()
