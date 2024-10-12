  * Soundcloud scraper to get recently posted tracks.
  * Manager uses multiprocessing and opens up a tab manager for each core, collecting all tracks before a certain date (date_diff)
  * Tab manager opens up an instance of selenium and scrapes a split of the total following list.
