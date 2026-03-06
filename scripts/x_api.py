#!/usr/bin/env python3
"""X (Twitter) API CLI for Kani-chan (@kani_chan0704)"""

from __future__ import print_function
import argparse
import json
import os
import sys

def _load_dotenv():
    search = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidate = os.path.join(search, ".env")
        if os.path.isfile(candidate):
            with open(candidate) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
            return
        search = os.path.dirname(search)

_load_dotenv()

import tweepy

# 認証情報
BEARER_TOKEN       = os.environ.get("X_BEARER_TOKEN", "")
API_KEY            = os.environ.get("X_API_KEY", "")
API_SECRET         = os.environ.get("X_API_SECRET", "")
ACCESS_TOKEN       = os.environ.get("X_ACCESS_TOKEN", "")
ACCESS_SECRET      = os.environ.get("X_ACCESS_SECRET", "")
OAUTH2_ACCESS_TOKEN = os.environ.get("X_OAUTH2_ACCESS_TOKEN", "")


def get_client_v2(write=False):
    """Tweepy Client (API v2) - OAuth1 User Contextで読み書き両対応"""
    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET,
        wait_on_rate_limit=True,
    )


def get_api_v1():
    """Tweepy API (v1.1) for operations not yet in v2"""
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True)

def user_auth_flag(write=False):
    """OAuth1 User Contextを使うので常にTrue"""
    return True


def ok(data):
    print(json.dumps({"ok": True, "data": data}, ensure_ascii=False, indent=2))


def err(msg):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False, indent=2))
    sys.exit(1)


# --- コマンド実装 ---

def cmd_tweet(args):
    """ツイートを投稿する"""
    client = get_client_v2(write=True)
    resp = client.create_tweet(text=args.text, user_auth=user_auth_flag(write=True))
    ok({"id": resp.data["id"], "text": args.text})


def cmd_reply(args):
    """リプライを投稿する"""
    client = get_client_v2(write=True)
    resp = client.create_tweet(text=args.text, in_reply_to_tweet_id=args.tweet_id, user_auth=user_auth_flag(write=True))
    ok({"id": resp.data["id"], "text": args.text, "reply_to": args.tweet_id})


def cmd_like(args):
    """ツイートにいいねする"""
    client = get_client_v2(write=True)
    resp = client.like(tweet_id=args.tweet_id, user_auth=user_auth_flag(write=True))
    ok({"liked": resp.data.get("liked", True), "tweet_id": args.tweet_id})


def cmd_unlike(args):
    """いいねを取り消す"""
    client = get_client_v2(write=True)
    resp = client.unlike(tweet_id=args.tweet_id, user_auth=user_auth_flag(write=True))
    ok({"unliked": True, "tweet_id": args.tweet_id})


def cmd_follow(args):
    """ユーザーをフォローする（username または user_id）"""
    write_client = get_client_v2(write=True)
    read_client = get_client_v2()
    me = write_client.get_me()
    my_id = me.data.id

    if args.user_id:
        target_id = args.user_id
    else:
        user = read_client.get_user(username=args.username, user_auth=True)
        if not user.data:
            err("User not found: " + args.username)
            return
        target_id = user.data.id

    resp = write_client.follow_user(target_user_id=target_id, user_auth=user_auth_flag(write=True))
    ok({"following": resp.data.get("following", True), "target_id": str(target_id)})


def cmd_unfollow(args):
    """フォローを解除する"""
    write_client = get_client_v2(write=True)
    read_client = get_client_v2()

    if args.user_id:
        target_id = args.user_id
    else:
        user = read_client.get_user(username=args.username, user_auth=True)
        if not user.data:
            err("User not found: " + args.username)
            return
        target_id = user.data.id

    resp = write_client.unfollow_user(target_user_id=target_id, user_auth=user_auth_flag(write=True))
    ok({"unfollowed": True, "target_id": str(target_id)})


def cmd_my_tweets(args):
    """自分の直近ツイートを取得"""
    client = get_client_v2()
    me = client.get_me(user_auth=True)
    user_id = me.data.id

    tweets = client.get_users_tweets(
        id=user_id,
        max_results=args.count,
        tweet_fields=["created_at", "public_metrics", "in_reply_to_user_id"],
        user_auth=True,
    )
    results = []
    if tweets.data:
        for t in tweets.data:
            results.append({
                "id": t.id,
                "text": t.text,
                "created_at": str(t.created_at) if t.created_at else None,
                "metrics": t.public_metrics,
            })
    ok(results)


def cmd_user_tweets(args):
    """指定ユーザーの直近ツイートを取得"""
    client = get_client_v2()

    if args.user_id:
        user_id = args.user_id
    else:
        user = client.get_user(username=args.username, user_auth=True)
        if not user.data:
            err("User not found: " + args.username)
            return
        user_id = user.data.id

    tweets = client.get_users_tweets(
        id=user_id,
        max_results=args.count,
        tweet_fields=["created_at", "public_metrics"],
        user_auth=True,
    )
    results = []
    if tweets.data:
        for t in tweets.data:
            results.append({
                "id": t.id,
                "text": t.text,
                "created_at": str(t.created_at) if t.created_at else None,
                "metrics": t.public_metrics,
            })
    ok(results)


def cmd_search(args):
    """ツイートを検索（最近7日間）"""
    client = get_client_v2()
    tweets = client.search_recent_tweets(
        query=args.query,
        max_results=args.count,
        tweet_fields=["created_at", "public_metrics", "author_id"],
    )
    results = []
    if tweets.data:
        for t in tweets.data:
            results.append({
                "id": t.id,
                "text": t.text,
                "author_id": str(t.author_id),
                "created_at": str(t.created_at) if t.created_at else None,
                "metrics": t.public_metrics,
            })
    ok(results)


def cmd_timeline(args):
    """ホームタイムラインを取得"""
    client = get_client_v2()
    me = client.get_me(user_auth=True)
    user_id = me.data.id

    tweets = client.get_home_timeline(
        max_results=args.count,
        tweet_fields=["created_at", "public_metrics", "author_id"],
        user_auth=True,
    )
    results = []
    if tweets.data:
        for t in tweets.data:
            results.append({
                "id": t.id,
                "text": t.text,
                "author_id": str(t.author_id),
                "created_at": str(t.created_at) if t.created_at else None,
            })
    ok(results)


def cmd_get_tweet(args):
    """ツイートIDからツイートを取得"""
    client = get_client_v2()
    tweet = client.get_tweet(
        id=args.tweet_id,
        tweet_fields=["created_at", "public_metrics", "author_id", "in_reply_to_user_id"],
    )
    if not tweet.data:
        err("Tweet not found: " + args.tweet_id)
        return
    t = tweet.data
    ok({
        "id": t.id,
        "text": t.text,
        "author_id": str(t.author_id),
        "created_at": str(t.created_at) if t.created_at else None,
        "metrics": t.public_metrics,
    })


def cmd_me(args):
    """自分のアカウント情報を取得"""
    client = get_client_v2()
    me = client.get_me(user_fields=["public_metrics", "description"])
    u = me.data
    ok({
        "id": str(u.id),
        "name": u.name,
        "username": u.username,
        "metrics": u.public_metrics,
        "description": u.description,
    })


# --- エントリポイント ---

def main():
    parser = argparse.ArgumentParser(description="X API CLI for @kani_chan0704")
    sub = parser.add_subparsers(dest="command")

    # tweet
    p_tweet = sub.add_parser("tweet", help="ツイートを投稿")
    p_tweet.add_argument("text", help="ツイート本文")

    # reply
    p_reply = sub.add_parser("reply", help="リプライを投稿")
    p_reply.add_argument("tweet_id", help="リプライ先のツイートID")
    p_reply.add_argument("text", help="リプライ本文")

    # like
    p_like = sub.add_parser("like", help="いいね")
    p_like.add_argument("tweet_id", help="いいねするツイートID")

    # unlike
    p_unlike = sub.add_parser("unlike", help="いいねを取り消す")
    p_unlike.add_argument("tweet_id", help="ツイートID")

    # follow
    p_follow = sub.add_parser("follow", help="フォローする")
    g_follow = p_follow.add_mutually_exclusive_group(required=True)
    g_follow.add_argument("--username", help="ユーザー名（@なし）")
    g_follow.add_argument("--user-id", dest="user_id", help="ユーザーID")

    # unfollow
    p_unfollow = sub.add_parser("unfollow", help="フォローを解除する")
    g_unfollow = p_unfollow.add_mutually_exclusive_group(required=True)
    g_unfollow.add_argument("--username", help="ユーザー名（@なし）")
    g_unfollow.add_argument("--user-id", dest="user_id", help="ユーザーID")

    # my_tweets
    p_mine = sub.add_parser("my-tweets", help="自分の直近ツイートを確認")
    p_mine.add_argument("--count", type=int, default=10, help="取得件数（最大100）")

    # user_tweets
    p_user = sub.add_parser("user-tweets", help="指定ユーザーのツイートを取得")
    g_user = p_user.add_mutually_exclusive_group(required=True)
    g_user.add_argument("--username", help="ユーザー名（@なし）")
    g_user.add_argument("--user-id", dest="user_id", help="ユーザーID")
    p_user.add_argument("--count", type=int, default=10, help="取得件数")

    # search
    p_search = sub.add_parser("search", help="ツイートを検索（直近7日間）")
    p_search.add_argument("query", help="検索クエリ")
    p_search.add_argument("--count", type=int, default=10, help="取得件数")

    # timeline
    p_timeline = sub.add_parser("timeline", help="ホームタイムラインを取得")
    p_timeline.add_argument("--count", type=int, default=20, help="取得件数")

    # get-tweet
    p_get = sub.add_parser("get-tweet", help="ツイートIDからツイートを取得")
    p_get.add_argument("tweet_id", help="ツイートID")

    # me
    sub.add_parser("me", help="自分のアカウント情報")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "tweet": cmd_tweet,
        "reply": cmd_reply,
        "like": cmd_like,
        "unlike": cmd_unlike,
        "follow": cmd_follow,
        "unfollow": cmd_unfollow,
        "my-tweets": cmd_my_tweets,
        "user-tweets": cmd_user_tweets,
        "search": cmd_search,
        "timeline": cmd_timeline,
        "get-tweet": cmd_get_tweet,
        "me": cmd_me,
    }

    try:
        dispatch[args.command](args)
    except tweepy.TweepyException as e:
        err("Tweepy error: " + str(e))
    except Exception as e:
        err("Error: " + str(e))


if __name__ == "__main__":
    main()
