<?php
ini_set("memory_limit", "2048M");

function get_replying_ids ($tweetid, $username) {
  global $replyingids; # Holds the Twitter IDs

  $maxposition = "";

  do {
    # Gets the url of the twitter post
    if ($maxposition == "") {
      $url = "https://twitter.com/" . $username . "/status/" . $tweetid;
    }
    else {
      $url = "https://twitter.com/i/" . $username . "/conversation/" . $tweetid . "?include_available_features=1&include_entities=1&max_position=" . $maxposition;
    }

    # Gets the html of the twitter post
    $content = shell_exec("wget \"" . $url . "\" -q --load-cookies=./cookies.txt -O -");
    $content = html_entity_decode(str_replace("\\n", "\n", $content));
    $content = str_replace("\\u003c", "<", $content);
    $content = str_replace("\\u003e", ">", $content);
    $content = str_replace("\\/", "/", $content);
    $content = str_replace("\\\"", "\"", $content);
    if (preg_match_all("|<a href=\"(/[^/]*/status/[0-9]*)\" class=\"tweet-timestamp js-permalink js-nav js-tooltip\"|U", $content, $reptweets)) {
      foreach ($reptweets[1] as $key => $reptweet) {
        $reptweettokens = explode("/", $reptweet);
        $repusername = $reptweettokens[1];
        $reptweetid = $reptweettokens[count($reptweettokens) - 1];

        if (!in_array($reptweetid, $replyingids)) {
          array_push($replyingids, $reptweetid);
          get_replying_ids($reptweetid, $repusername);
        }
      }
    }

    $maxposition = "";
    if (preg_match("|data-min-position=\"([^\"]*)\"|U", $content, $mp) || preg_match("|\"min_position\":\"([^\"]*)\"|U", $content, $mp)) {
      $maxposition = $mp[1];
    }
  } while ($maxposition != "");
  print("Finished with ID: " . $tweetid . " for user: " . $username . "\n");
}

function add_to_structure ($tweetid, $inreplyto) {
  global $structure;

  foreach ($structure as $id => $substructure) {
    if ($id == $inreplyto) {
      $structure[$id] = $tweetid;
    }
    else {
      add_to_structure($tweetid, $inreplyto, $structure[$id]);
    }
  }
}

function collect_replying_tweets ($tweetid, $username) {
  global $argv, $replyingids;
  $replycount = 0;

  # Creates the data/reaction folder for the particular twitter post
  shell_exec(mkdir("data/" . $tweetid . "/reactions/"));
  shell_exec(chmod("data/" . $tweetid . "/reactions/", 0777));
  get_replying_ids($tweetid, $username);
  $idsstr = "";
  $idcount = 0;
  $allcount = 0;
  # Iterates through each each Twitter ID and runs the retrieve.tweet.py file
  # This is where currently my problem lies
  # Look at the original file. For some reason they were using the retrieve.tweet.list. py
  # file and I don't know why and had to get rid of a for loop
  # See why they did their way
  foreach ($replyingids as $replyingid) {
    print($replyingid . "\n");
    $allcount++;
    $idsstr .= $replyingid . ",";
    $idcount++;
    if ($idcount == 1 || $allcount == count($replyingids)) {
      print("Inputing tweet ID: " . substr($idsstr, 0, strlen($idsstr) - 1) . "\n");
      $tweets = shell_exec("python retrieve.tweet.py " . $replyingid);
      $tweetobj = json_decode($tweets);
      if (isset($tweetobj->id_str)) {
        print($tweetobj->id_str . "\n");
        file_put_contents("data/" . $tweetid . "/reactions/" . $tweetobj->id_str . ".json", $tweetobj);
        $replycount++;
      }
      $idsstr = "";
      $idcount = 0;
    }
  }

  if (isset($argv[1])) {
    echo $tweetid . " - source tweet and " . $replycount . " replies collected.\n";
  }
}

function create_structure($tweetid) {
  global $structure;

  $parents = array();
  $dir = dir("data/" . $tweetid . "/reactions/");
  while (($file = $dir->read()) !== false) {
    if ($file != "." && $file != "..") {
      $tweet = json_decode(file_get_contents("data/" . $tweetid . "/reactions/" . $file));

      $inreplyto = $tweet->in_reply_to_status_id_str;
      $id = $tweet->id;

      if (!isset($parents[$inreplyto])) {
        $parents[$inreplyto] = array();
      }
      array_push($parents[$inreplyto], $id);
    }
  }

  foreach ($structure as $sid => $substructure) {
    if (isset($parents[$sid])) {
      foreach ($parents[$sid] as $cid) {
        $structure[$sid][$cid] = array();
      }
    }
  }

  file_put_contents("data/" . $tweetid . "/structure.json", json_encode($structure));
  chmod("data/" . $tweetid . "/structure.json", 0777);
}

if (!isset($argv[1])) {
  exit(0);
}
$tweetid = $argv[1];

if (strstr($tweetid, "/")) {
  $tweetid = explode("/", $tweetid);
  $tweetid = $tweetid[count($tweetid) - 1];
}

$replyingids = array();
$structure = array($tweetid => array());
print("Tweet ID: " . $tweetid . "\n");
# Takes the Twitter ID and run the retrive.tweet.py script and return a json file
$sourcetweet = shell_exec("python retrieve.tweet.py " . $tweetid);
# Decodes the Json file into an array
print("Source Tweet: " . $sourcetweet . "\n");
$sourcetweetobj = json_decode($sourcetweet);

# Checks to see if there is an id in the array
if (isset($sourcetweetobj->id_str)) {
  
  # Finds the username of the Twitter ID
  $username = $sourcetweetobj->user->screen_name;
  print($username);
  # Creates the source-tweets folder and saves the tweet in a json file
  shell_exec(mkdir("data/" . $tweetid));
  shell_exec(chmod("data/" . $tweetid, 0766));
  shell_exec(mkdir("data/" . $tweetid . "/source-tweets/"));
  shell_exec(chmod("data/" . $tweetid . "/source-tweets/", 0766));
  file_put_contents("data/" . $tweetid . "/source-tweets/" . $tweetid . ".json", $sourcetweet);

  # Runs the collect_replying_tweets function to find the tweets that reply
  # to the inputed Twitter post
  collect_replying_tweets($tweetid, $username);

  # Creates the structure on how the tweet was replied to
  create_structure($tweetid);
}
?>
