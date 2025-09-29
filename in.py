#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# INSTA-RECON: Advanced OSINT for Instagram targets

import requests
import json
import argparse
import os
import re
import html
import time

# ---[ COLORS ]------------------------------------------------------------------
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"

# ---[ HELPERS ]-----------------------------------------------------------------

def print_banner():
    """Prints a cool banner."""
    banner = f"""
{Colors.BOLD}{Colors.MAGENTA}

╦╔╗╔╗╦╔═╗╔═╗╔═╗╔═╗╔╗╔
║║║╠╣║╚═╗╠═╣╠═╝╠═╣║║║
╩╩╝╝╝╩╚═╝╩ ╩╩  ╩ ╩╝╚╝
{Colors.CYAN}INSTA-RECON-by-nero v2.2 - Advanced OSINT Tool{Colors.RESET}
"""
    print(banner)

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}[+] {title.upper()}{Colors.RESET}")

def print_field(field_name, value, color=Colors.GREEN):
    print(f"    {Colors.YELLOW}{field_name:<12}:{color} {value}{Colors.RESET}")

def create_output_directory(username):
    """Creates a dedicated directory for the target's recon files."""
    dir_name = f"{username}_recon"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

# ---[ DATA ANALYSIS & EXTRACTION ]----------------------------------------------

def download_profile_picture(user_data, output_dir):
    """Downloads the user's HD profile picture."""
    pic_url = user_data.get('profile_pic_url_hd')
    if not pic_url:
        print(f"{Colors.YELLOW}[-] No HD profile picture URL found.{Colors.RESET}")
        return None

    try:
        print("[*] Downloading profile picture...")
        response = requests.get(pic_url)
        response.raise_for_status()
        file_path = os.path.join(output_dir, f"{user_data.get('username')}_profile_pic.jpg")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"{Colors.GREEN}[+] Profile picture saved to {file_path}{Colors.RESET}")
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}[-] Failed to download profile picture: {e}{Colors.RESET}")
    return None

def analyze_bio(bio):
    """Extracts emails, hashtags, and mentions from bio text."""
    if not bio:
        return None, None, None

    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', bio)
    hashtags = re.findall(r'#(\w+)', bio)
    mentions = re.findall(r'@(\w+)', bio)
    
    return emails, hashtags, mentions

# ---[ REPORTING ]----------------------------------------------------------------

def generate_html_report(user_data, output_dir, pic_path):
    """Generates a self-contained HTML report."""
    print("[*] Generating HTML report...")
    username = user_data.get('username', 'N/A')
    full_name = user_data.get('full_name', 'N/A')
    bio = user_data.get('biography', 'N/A')
    emails, hashtags, mentions = analyze_bio(bio)
    posts = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])

    # Pre-calculate stats
    stats_posts = user_data.get('edge_owner_to_timeline_media', {}).get('count', 0)
    stats_followers = user_data.get('edge_followed_by', {}).get('count', 0)
    stats_following = user_data.get('edge_follow', {}).get('count', 0)
    stats_verified = "Yes" if user_data.get('is_verified') else "No"

    # Sanitize for HTML
    full_name = html.escape(full_name)
    bio_html = html.escape(bio).replace('\n', '<br>')

    # Linkify bio
    if emails:
        for email in emails:
            bio_html = bio_html.replace(email, f'<a href="mailto:{email}">{email}</a>')
    if hashtags:
        for tag in hashtags:
            bio_html = bio_html.replace(f'#{tag}', f'<a href="https://www.instagram.com/explore/tags/{tag}/" target="_blank">#{tag}</a>')
    if mentions:
        for mention in mentions:
            bio_html = bio_html.replace(f'@{mention}', f'<a href="https://www.instagram.com/{mention}/" target="_blank">@{mention}</a>')

    posts_html = ""
    if user_data.get('is_private'):
        posts_html = "<p><i>Account is private. Posts are not available.</i></p>"
    elif posts:
        for post_edge in posts:
            post = post_edge.get('node', {})
            post_url = f"https://www.instagram.com/p/{post.get('shortcode')}"
            caption = post.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', 'No caption')
            likes = post.get('edge_media_preview_like', {}).get('count', 0)
            comments = post.get('edge_media_to_comment', {}).get('count', 0)
            thumb_url = post.get('thumbnail_src')
            posts_html += f'''
                <div class="post">
                    <a href="{post_url}" target="_blank"><img src="{thumb_url}" alt="Post thumbnail"></a>
                    <div class="post-info">
                        <p><b>Likes:</b> {likes} | <b>Comments:</b> {comments}</p>
                        <p>{html.escape(caption)}</p>
                    </div>
                </div>
            '''

    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Insta-Recon Report: {username}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; background-color: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.5); }}
            h1, h2 {{ color: #bb86fc; border-bottom: 2px solid #bb86fc; padding-bottom: 10px; }}
            .header {{ display: flex; align-items: center; }}
            .header img {{ border-radius: 50%; width: 100px; height: 100px; margin-right: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
            .stat {{ background-color: #333; padding: 15px; border-radius: 5px; text-align: center; }}
            .stat .value {{ font-size: 1.5em; font-weight: bold; color: #03dac6; }}
            .bio {{ background-color: #333; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            .post {{ display: flex; background-color: #333; padding: 10px; border-radius: 5px; margin-bottom: 10px; align-items: center; }}
            .post img {{ width: 150px; height: 150px; object-fit: cover; border-radius: 5px; margin-right: 15px; }}
            a {{ color: #03dac6; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="{os.path.basename(pic_path) if pic_path else ''}" alt="Profile Picture">
                <h1>{full_name} (@{username})</h1>
            </div>

            <h2>Profile Stats</h2>
            <div class="stats-grid">
                <div class="stat"><div>Posts</div><div class="value">{stats_posts}</div></div>
                <div class="stat"><div>Followers</div><div class="value">{stats_followers}</div></div>
                <div class="stat"><div>Following</div><div class="value">{stats_following}</div></div>
                <div class="stat"><div>Verified</div><div class="value">{stats_verified}</div></div>
            </div>

            <h2>Biography</h2>
            <div class="bio">
                <p>{bio_html}</p>
            </div>

            <h2>Recent Posts</h2>
            {posts_html}

        </div>
    </body>
    </html>
    '''
    
    try:
        report_path = os.path.join(output_dir, "report.html")
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(html_content)
        print(f"{Colors.GREEN}[+] HTML report saved to {report_path}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[-] Failed to generate HTML report: {e}{Colors.RESET}")

# ---[ DISPLAY FUNCTIONS ]-------------------------------------------------------

def display_summary(user):
    """Displays the main summary of the user's profile."""
    print_section("User Summary")
    print_field("Full Name", user.get('full_name', 'N/A'))
    print_field("Username", user.get('username', 'N/A'))
    print_field("User ID", user.get('id', 'N/A'))
    print_field("Verified", user.get('is_verified', False), Colors.MAGENTA if user.get('is_verified') else Colors.GREEN)
    print_field("Private", user.get('is_private', False), Colors.RED if user.get('is_private') else Colors.GREEN)
    
    print_section("Profile Stats")
    print_field("Posts", user.get('edge_owner_to_timeline_media', {}).get('count', 0))
    print_field("Followers", user.get('edge_followed_by', {}).get('count', 0))
    print_field("Following", user.get('edge_follow', {}).get('count', 0))

def display_extended_info(user):
    """Displays bio, contact info, and other extracted details."""
    print_section("Biography & Contact")
    bio = user.get('biography', 'N/A')
    emails, hashtags, mentions = analyze_bio(bio)

    if bio:
        print(f"    {Colors.GREEN}{bio}{Colors.RESET}")
    else:
        print(f"    {Colors.YELLOW}No biography found.{Colors.RESET}")

    if emails:
        print_field("Emails", ", ".join(emails), color=Colors.RED)
    if hashtags:
        print_field("Hashtags", f"#{ ' #'.join(hashtags)}")
    if mentions:
        print_field("Mentions", f"@{ ' @'.join(mentions)}")

def display_recent_posts(user):
    """Displays the user's most recent posts."""
    print_section("Recent Posts")
    if user.get('is_private'):
        print(f"    {Colors.YELLOW}Cannot view posts, account is private.{Colors.RESET}")
        return

    posts = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
    if not posts:
        print(f"    {Colors.YELLOW}No posts found.{Colors.RESET}")
        return

    for i, post_edge in enumerate(posts):
        post = post_edge.get('node', {})
        post_url = f"https://www.instagram.com/p/{post.get('shortcode')}"
        caption = post.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', 'No caption')
        likes = post.get('edge_media_preview_like', {}).get('count', 0)
        comments = post.get('edge_media_to_comment', {}).get('count', 0)
        
        print(f"    {Colors.BOLD}{Colors.MAGENTA}Post #{i+1}{Colors.RESET} - {Colors.CYAN}{post_url}{Colors.RESET}")
        print(f"      {Colors.YELLOW}Likes:{Colors.GREEN} {likes} {Colors.YELLOW}Comments:{Colors.GREEN} {comments}{Colors.RESET}")
        print(f"      {Colors.YELLOW}Caption:{Colors.GREEN} {caption[:80].replace('\n', ' ')}...{Colors.RESET}")

# ---[ CORE FUNCTIONS ]----------------------------------------------------------

def fetch_user_data(username, headers):
    """Fetches the user's data from Instagram's API."""
    print(f"[*] Fetching data for {Colors.BOLD}{username}{Colors.RESET}...")
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        user = data.get('data', {}).get('user')
        if not user:
            print(f"{Colors.RED}[-] Could not find user data for '{username}'. Account may not exist.{Colors.RESET}")
            return None
        print(f"{Colors.GREEN}[+] Data fetched successfully!{Colors.RESET}")
        return user
    except requests.exceptions.HTTPError as http_err:
        print(f"{Colors.RED}[-] HTTP error occurred: {http_err} - Account may not exist or is private.{Colors.RESET}")
    except requests.exceptions.RequestException as req_err:
        print(f"{Colors.RED}[-] Network error occurred: {req_err}{Colors.RESET}")
    except json.JSONDecodeError:
        print(f"{Colors.RED}[-] Failed to parse JSON. API structure may have changed.{Colors.RESET}")
    return None

def insta_recon(username, no_html=False):
    """Main orchestration function."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'X-IG-App-ID': '936619743392459'
    }
    user_data = fetch_user_data(username, headers)
    if not user_data:
        return

    # Create output directory
    output_dir = create_output_directory(username)
    print(f"[*] Saving recon files to {Colors.BOLD}{output_dir}/{Colors.RESET}")

    # Display primary data
    display_summary(user_data)
    display_extended_info(user_data)
    display_recent_posts(user_data)

    # Download profile picture
    pic_path = download_profile_picture(user_data, output_dir)

    # Save JSON report
    report_file = os.path.join(output_dir, f"{username}_recon.json")
    with open(report_file, "w", encoding='utf-8') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)
    print(f"\n{Colors.GREEN}[+] Full JSON report saved to {report_file}{Colors.RESET}")

    # Generate HTML report
    if not no_html:
        generate_html_report(user_data, output_dir, pic_path)

def main():
    """Main entry point and argument parsing."""
    parser = argparse.ArgumentParser(
        description="INSTA-RECON: An advanced OSINT tool for Instagram.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-u", "--username", help="A single Instagram username to scan.")
    parser.add_argument("-f", "--file", help="Path to a file containing a list of usernames to scan (one per line).")
    parser.add_argument("--no-html", action="store_true", help="Disable HTML report generation.")
    
    print_banner()
    print(f"{Colors.BOLD}{Colors.YELLOW}[!] FOR AUTHORIZED TESTING ONLY. YOU ARE RESPONSIBLE FOR COMPLIANCE.{Colors.RESET}\n")

    args = parser.parse_args()
    
    if args.username:
        insta_recon(args.username, args.no_html)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
            print(f"[*] Loaded {len(usernames)} usernames from {args.file}")
            for i, username in enumerate(usernames):
                print(f"\n--- Processing target {i+1} of {len(usernames)}: {username} ---")
                insta_recon(username, args.no_html)
                if i < len(usernames) - 1:
                    print("[*] Sleeping for 2 seconds to avoid rate-limiting...")
                    time.sleep(2)
        except FileNotFoundError:
            print(f"{Colors.RED}[-] Error: The file '{args.file}' was not found.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[-] An error occurred while processing the file: {e}{Colors.RESET}")
    else:
        parser.print_help()

# ---[ MAIN EXECUTION ]----------------------------------------------------------

if __name__ == "__main__":
    main()
