# Display subreddit traffic statistics.

# This program takes the output from :meth:`~.Subreddit.traffic` and neatly
# displays it in an ASCII table.

# There are three types of subreddit traffic that are returned.

# 1. Traffic per month
# 2. Traffic per day
# 3. Traffic per hour

# Each value contains the amount of pageviews, unique pageviews, and
# subscribers in the particular time frame.

# Months will be displayed in the `monthname year` format.
# Days will be displayed in your locale's default settings
# Hours will be displayed in the `time date` format, in 24-hour time.

from datetime import datetime

from praw import Reddit


def make_table(rows, tabletype):
    """Makes an ASCII table"""
    # Note: Hour format does not have the subscribers count
    rowlength = len(rows[0])
    col1 = tabletype
    col2 = "Unique Pageviews"
    col3 = "Total Pageviews"
    col4 = "Subscribers"
    # This line gets the time value that is the longest
    max_length_1 = max(len(data[0]) for data in rows)
    # This line gets the largest total pageview count
    max_length_2 = max(len(str(data[1])) for data in rows)
    # This line gets the largest unique pageview count
    max_length_3 = max(len(str(data[2])) for data in rows)
    # This line gets the largest subscriber count
    max_length_4 = (
        max(len(str(data[3])) for data in rows) if rowlength == 4 else None
    )
    # This line makes sure that the max lengths are the size of the headers
    max_length_1 = max_length_1 if len(col1) <= max_length_1 else len(col1)
    max_length_2 = max_length_2 if len(col2) <= max_length_2 else len(col2)
    max_length_3 = max_length_3 if len(col3) <= max_length_3 else len(col3)
    if rowlength == 4:
        max_length_4 = max_length_4 if len(col4) <= max_length_4 else len(col4)
    # This line defines the template for each row
    row_template = "| %-{}s | %-{}s | %-{}s |".format(
        max_length_1, max_length_2, max_length_3
    )
    if rowlength == 4:
        row_template += " %-{}s |".format(max_length_4)
    seperator = (
        "|-"
        + "-" * max_length_1
        + "-|-"
        + "-" * max_length_2
        + "-|-"
        + "-" * max_length_3
    )
    seperator += "-|-" + "-" * max_length_4 + "-|" if rowlength == 4 else "-|"
    # Prints the header
    print(seperator.replace("-", "="))
    print(
        row_template % (col1, col2, col3, col4)
        if rowlength == 4
        else row_template % (col1, col2, col3)
    )
    print(seperator.replace("-", "="))
    for row in rows:
        print(row_template % row)
        print(seperator)


def timestamps_to_strings(rows, format):
    return [
        (datetime.fromtimestamp(row[0]).strftime(format), *row[1:])
        for row in rows
    ]


def main():
    # Create your Reddit instance
    reddit = Reddit(
        username="username",  # Replace with your username
        password="Password",  # Replace with your password
        client_id="Client_ID",  # Replace with your client ID
        client_secret="Client_Secret",  # Replace with your client secret
        user_agent="User_Agent",  # Replace with your user agent
    )

    # Pick a subreddit that you moderate
    subreddit = reddit.subreddit("test")

    traffic_data = subreddit.traffic()

    formats = {"hour": "%X %x", "day": "%x", "month": "%B %Y"}

    for timetype, rows in traffic_data.items():
        newrows = timestamps_to_strings(rows, formats[timetype])
        make_table(newrows, timetype)
        print("\n")


if __name__ == "__main__":
    main()
