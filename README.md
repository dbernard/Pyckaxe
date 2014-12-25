# Pyckaxe

Pyckaxe is a helpful data mining tool for both gathering potentially large
volumes of tweets from the Twitter public stream as well as parsing and graphing
the results.

This project utilizes the [Twitter Streaming API](https://dev.twitter.com/streaming/overview)
and [Tweepy](http://www.tweepy.org/).


### Important Notes

* **Performance:** This is a work in progress. There are various performance and
  parsing improvements to be made!

* **Databases:** The default listener uses sqlite3 databases and there is
  currently no functionality to update database schemas if/when they change.
  This means old databases *may* not work as expected. We will probably need to
  address this in the future.


### Usage

Pyckaxe can be used standalone or imported into another project. Users can
deploy their own custom StreamListeners to Pyckaxe to handle incoming tweet data
however they wish.

The default listener will store the Tweet ID, text, creation time, and
coordinates in an sqlite database. When importing Pyckaxe, this database may be
given a custom path. When used standalone, the database will be stored in a
`database/` directory in the Pyckaxe directory.

**For standalone usage:**

1. Create an application on Twitter and obtain your consumer/access tokens. (for
more information on creating a new application, see [here](https://dev.twitter.com/)).

2. Once you have obtained your tokens, place them in a CSV file,
   "credentials.csv" with the following format:

   ```
   consumer_key,YOUR_CONSUMER_KEY_HERE
   consumer_secret,YOUR_CONSUMER_SECRET_HERE
   access_token,YOUR_ACCESS_TOKEN_HERE
   access_secret,YOUR_ACCESS_SECRET_HERE
   ```

   If you are using [Plotly][https://plot.ly/] for any data graphing, include
   the following lines in the "credentials.csv" file:

   ```
   plotly_username,YOUR_PLOTLY_USERNAME_HERE
   plotly_api_key,YOUR_PLOTLY_API_KEY_HERE
   ```

   *Warning: Keep your keys/tokens a secret!*

3. From the command line, run pyckaxe.py with the terms you wish to collect
   tweets about. You can also provide a database name. If you do not, you will
   be prompted for one:
    ```
    python pyckaxe.py "YOUR SEARCH TERMS HERE" --database=DB_NAME.db
    ```

4. Collect tweets for however long you wish. Tweets collected since running and
   database file size (in KB) will be shown at the command line. Exit with
   ctrl-c.

5. Run one of the parsing scripts to parse/graph the data.


**To use Pyckaxe as an object:**

1. See step #1 above - This is required for any Application that wants to access
   the Twitter Streaming API.

2. Once you have your consumer key/secret and access token/secret, store them
   however you'd like, but remember to keep them secret/safe. Regardless of how
   your store them, Pyckaxe will require that that be in a dictionary with the
   keys `consumer_key`, `consumer_secret`, `access_token`, and `access_secret`
   when you create your Pyckaxe object.

3. Initialize your custom listener or the default `Pyckaxe.CollectListener`.

4. Create a Pyckaxe object. `terms` must be a list. Ex:

   ```python
   terms = ['football']
   pyck = Pyckaxe(listener, terms, credentials)
   ```

5. To begin collection, call `gather(async=True)` on your Pyckaxe object.
   **NOTE:** If you are **not** using this standalone, you will *probably* need
   to set the `async` parameter to True so that it does not block the rest of
   your application and force you to ctrl-c out of it to stop collection.

6. If you set `async=True`, tweet collection can be halted at any time by
   calling the `stop()` method on your Pyckaxe object (Ex: `pyck.stop()`).

   Please note that this does **NOT** handle the closing of any listener
   objects, so if your custom listener requires a graceful exit, do so after
   calling `stop()`. If using the default `Pyckaxe.CollectListener`, it is
   recommended that you call `close()` on your listener object after stopping to
   gracefully disconnect from the database unless you intend to call `gather()`
   again.


### Custom Listeners

Custom listeners **must** derive from the Tweepy `StreamListener`. For more
information, see [here](https://github.com/tweepy/tweepy/blob/master/examples/streaming.py).


### Parsing/Graphing Data

Keep in mind that parsing and graphing data is a constantly growing effort in
this tool. There are many improvements and new parsing/graphing methods to be
explored.

Below are explanations of how to use the various parsing and graphing tools.


#### Graphing: Word Frequency

To collect word frequencies standalone, you can run `python word_freq.py
(number-of-results) --database=(database-name)`. This requires that you used the
default listener to collect tweets.

If you have used your own listener, you can generate word frequencies via a
`WordFreq` object. Create the object, then add your data to the object via calls
to `add_data()`. When all data is added, call `get_results(n)` to get the `n`
most frequently used words.


#### Graphing: Word Cloud

To generate a word cloud standalone, you can run `python word_cloud.py
--name=(image-name) --database=(database-name)`. Again, any standalone
execution requires that you had used the default listener to collect tweets.

If you have used your own listener, you can generate a word cloud via a
`WordCloudBuilder` object. Just like with the word frequencies, you can add data
to the word cloud builder via calls to `add_data()`. When you have all your
data added, you can call `generate_wordcloud(filename, [bg_color='white',
color_func=monochrome_color_func])` to generate a word cloud image at the path
provided by your `filename` argument.


#### Graphing: Sentiment Analysis

**IMPORTANT:** *This is a* **VERY** *naive implementation of sentiment
analysis. Sentiment analysis is a very complex subject, and I have no
intention of covering all the intricacies involved.*

*Instead, this project employs more of a "shotgun" approach - While this
implementation of sentiment analysis may not be very accurate for a small
amount of information, the hope is that with very large sets of information we
will get a generally accurate result.*

*We also currently only support English language input.* **Be warned,** *this
results in a lot of neutral results (for example, a Spanish language tweet
will be classified as neutral, regardless of what it says), so use the neutral
result at your own risk.*

To run sentiment analysis standalone, you can run `python sentiment.py
--database=(database-name) --plotbars=(graph-image-name)`. You can leave off the
`plotbars` argument if you do not want to graph the data, in which case the
positive, negative, and neutral counts will be printed. Otherwise, the data will
be graphed through Plotly.

If you have used your own listener to collect tweets, sentiment analysis can be
done in much the same way as the other tools. Create a `SentimentAnalysis`
object and add data to it via calls to `add_text()`. When all text is added, a
call to `get_sentiment(graph=[True or False], filename, title)`.

