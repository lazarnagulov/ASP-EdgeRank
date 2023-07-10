# ASP-EdgeRank
This project represents my implementation of EdgeRank algorithm which recommends posts on a social network.

The project consists of a graph which has the social network's users as vertices and their affinity as the edges, as well as my implementation of a trie which is stores all words from all statuses that users have posted.

# Usage
Run aplication with `python3 ./src/App.py`. After the datasets has loaded, enter `start`. To view posts, enter a username from friends.csv. 
Now, you can search posts with `search`, or exit program with `exit`.

* To perform a case-insensitive search where any word matches the given term, input anything.
* To perform a case-sensitive search where all words match the given term in the given order, input the search term between double quotation marks ("x").
* To perform a word autocompletion search, input anything followed by *.

# Dependencies

```
networkx - pip install networkx
pickle - pip install pickle
```
