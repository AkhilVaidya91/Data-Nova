search_hashtags = ['Zomato']
# search_hashtags = None
hashtags = "['Zomato', 'aiueufb']"

for i in range(5):
    found = False
    if search_hashtags is not None:
        for hashtag in search_hashtags:
            hashtag = str(hashtag)
            hashtags = str(hashtags)
            if hashtag.lower() in hashtags.lower():
                ## continue normal execution
                found = True
                break
            else:
                found = False
    if found or search_hashtags is None:
        print('abcd')