#Grape Aphid#

It might seem like in this day and age ordering wine for shipment directly to your house without the state being involved wouldn't be worth much attention. But in Pennsylvania it's a brand-new thing.

Only recently could wineries apply to the Pennsylvania Liquor Control Board for a license to ship wine directly to consumers.

At this writing, there are 834 that have paid their $250 and gotten one since August 8. The rules are [a little weird](http://www.lcb.pa.gov/Legal/Documents/003492.pdf). Plus: The site where the state [lists them all](http://www.lcbapps.lcb.state.pa.us/webapp/Retail/Direct_Shippers_list.asp) is frightening. Just **10 results per page** and no way to manipulate anything into showing you more at a time. **There's no way to search or filter the data.** Or even to order the results better.

There's no information about websites or ordering or inventory. And companies apply for these licenses with their official business names -- not the label names of the wineries -- so it's not so simple to even search the PLCB's existing inventory for the same wines. I decided against writing a pure search function for this reason. Who would know what to search for?

Plus: Sometimes the number of shippers decreases. Sometimes the state's site goes down for what can be days at a time if there's a weekend involved. Even when it's all working correctly, try to use that thing on a phone.

That site also doesn't contain any last-modified data. It seems the data is just tossed up there unsorted in any way a user might care about. New entries don't go at the beginning. They don't go at the end. They don't go in the middle. I checked. And, y'know, I just don't know.

Which leads us to this project's name. The greatest plague on vineyards in history is [phylloxera](https://en.wikipedia.org/wiki/Phylloxera), which in its winged form is a relative of the aphid. I figured I was about to become a bit of a wine pest my own self. Plus also [this](https://www.youtube.com/watch?v=E8G5gSP64D4). And, well, here we are.

So I took part of a Sunday after [a friendly suggestion](https://twitter.com/andy_c/status/795097314734043136) that **there should be a better way** and wrote the initial scraper. Note that this is in `Python 3.6` -- playing with that some more was also part of the excuse for getting this little project going.

After that came a refactor for more contextual data using Google's geolocation API and to take advantage of generators to help things run a bit more smoothly.

The API is still missing on a few of the addresses it's given -- shippers self-report them and no one at the PLCB cleans them up -- but a hashmap can handle the ones we know about. The rest we log and update as we can. Meantime, there's enough error-handling so nothing really breaks until we can do that.

And, hey, now there's an actual map. (Yes, that's Hawaii off in the corner.)

![wine_map]

Right now the Python scraper just dumps to JSON and doesn't have a way to know what wineries it's already seen. That'll come later. It's set up to run on a cron job but doesn't yet. New businesses get added to the PLCB's list almost daily, but very few at a time. Might just run it weekly.

Sample data looks like this:

![sample_data]

Which, let's be real, is an improvement over this:

![plcb_site]

Once the scraper is done running and the file is created, [a Flask app](http://grapeaphid.com) looks for the most-recent file to use for data and another script creates a few bar charts from whichever data file we give it that show some of what's been most interesting in the data so far. To me, anyway.

More work to do -- it's already ripe for a cleaner refactor, among other things -- but for now, it does enough to get it out there. To come might well be some crowdsourcing to help figure out who these businesses really are and what they can send you. That would be lovely. It's not too realistic to do alone.

But most importantly, this data, as the Western Pennsylvania dialect would have it, needs liberated.

Let the fun begin:
```python
def run_the_jewels():
    '''
    a wrapper function to handle the scrape

    args: none

    returns: a list of lists, with each nested list representing
    one page of the scrape
    '''
    page = page_tools.Page()
    parser = page_tools.htmlParser()
    helper = sc.scrapeHelper()
    tree = parser.treeify(sc.set_base_url())
    total_shippers_string = helper.get_total_shippers_string(tree)
    total_shippers = helper.parse_total_shippers(total_shippers_string)
    urls = helper.url_generator(total_shippers)
    data = [page.get_winery_data(url) for url in urls]
    return data
```
[plcb_site]:https://github.com/thejqs/pa_wine_shippers/blob/master/plcb_wine_shippers.png

[sample_data]:https://github.com/thejqs/pa_wine_shippers/blob/master/json_sample.png

[wine_map]:https://github.com/thejqs/pa_wine_shippers/blob/master/wine_map.png
