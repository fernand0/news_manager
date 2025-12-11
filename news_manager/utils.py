from pathlib import Path
import logging

try:
    from socialModules import moduleRules
    from socialModules.configMod import safe_get
    SOCIALMODULES_AVAILABLE = True
except ImportError:
    SOCIALMODULES_AVAILABLE = False
    logging.warning("socialModules not available. Email source selection will not work.")


def select_from_list(options, identifier="", selector="", default=""):
    """
    Presents a list of options to the user and returns the selected option.
    """
    for i, option in enumerate(options):
        print(f"{i}) {option}")

    while True:
        try:
            selection = input("Select an option: ")
            if selection.isdigit():
                selection = int(selection)
                if 0 <= selection < len(options):
                    return selection, options[selection]
            elif selection.startswith('http'):
                return len(options)-1, selection
            else:
                for i, option in enumerate(options):
                    if selection.lower() in option.lower():
                        return i, option
        except (ValueError, IndexError):
            pass
        except (KeyboardInterrupt, EOFError):
            print("\nSelection cancelled.")
            return None, None
        print("Invalid selection. Please try again.")


def get_content_from_web(url=None):
    """
    Prompts user for a URL and returns it.

    Returns:
        Tuple of (url, source_description) or (None, None) if cancelled
    """
    try:
        if not url:
            url = input("Enter the URL of the news article: ").strip()
        if not url:
            print("No URL provided.")
            return None, None

        source_description = f"Web: {url}"
        return url, source_description
    except (KeyboardInterrupt, EOFError):
        print("\nInput cancelled.")
        return None, None


def select_news_source():
    """
    Presents a unified menu to select the news source (email accounts or web).
    Shows all available email accounts plus "Web (URL)" option at the end.

    Returns:
        Dictionary with keys:
            - 'type': 'email' or 'web'
            - 'content': content text (for email) or None (for web)
            - 'url': URL string (for web) or None
            - 'description': human-readable description of the source
            - 'api_src': API source object (for email) or None
        Returns None if selection was cancelled or failed.
    """
    print("\n--- Select news source ---")

    # Build list of available sources
    sources = []
    email_sources = []

    if SOCIALMODULES_AVAILABLE:
        try:
            rules = moduleRules.moduleRules()
            rules.checkRules()

            # Get all available email accounts (gmail and imap)
            api_src_types = ["gmail", "imap"]
            all_rules = rules.selectRule(api_src_types, "")

            for source_name in all_rules:
                source_details = rules.more.get(source_name, {})
                service_type = source_details.get('what', 'Email')
                sources.append(f"{source_name} ({service_type})")
                email_sources.append((source_name, source_details))

        except Exception as e:
            print(f"Warning: Could not load email sources: {e}")

    # Add web option at the end
    optionWebName = "Web (An URL is ok) "
    sources.append(optionWebName)

    if not sources or (len(sources) == 1 and sources[0] == optionWebName):
        print("Note: Only web sources are available (no email accounts configured)")

    # Let user select
    sel, selected = select_from_list(sources)

    if sel is None:
        return None

    # Check if web was selected (always the last option)
    if ((selected == optionWebName)
        or (selected.startswith('http'))):
        url = None
        if selected.startswith('http'):
            url = selected
        url, description = get_content_from_web(url)
        if url is None:
            return None
        return {
            'type': 'web',
            'content': None,
            'url': url,
            'description': description,
            'api_src': None
        }

    # Email account was selected
    if sel < len(email_sources):
        source_name, source_details = email_sources[sel]

        # Initialize the API source
        rules = moduleRules.moduleRules()
        api_src = rules.readConfigSrc("", source_name, source_details)

        if not api_src or not api_src.getClient():
            print(f"Failed to connect to {source_name}.")
            return None

        # Determine folder name based on service type
        folder = "INBOX/rrss" if "imap" in api_src.service.lower() else "rrss"

        api_src.setPostsType("posts")
        api_src.setLabels()
        label = api_src.getLabels(folder)

        if not label:
            print(f"No folder/label '{folder}' found in {source_name}.")
            return None

        api_src.setChannel(folder)
        api_src.setPosts()
        posts = api_src.getPosts()

        if not posts:
            print(f"No emails found in folder '{folder}' of {source_name}.")
            return None

        # Present emails to user for selection
        titles = [api_src.getPostTitle(post) for post in posts]
        print(f"\n--- Select an email from {folder} ({source_name}) ---")
        email_sel, post_title = select_from_list(titles)

        if email_sel is None:
            return None

        selected_post = posts[email_sel]
        post_body = api_src.getPostBody(selected_post)

        if isinstance(post_body, bytes):
            post_body = post_body.decode("utf-8")

        # Combine subject and body
        content_text = f"Subject: {post_title}\n\n{post_body}"
        source_description = f"Email from {source_name}: {post_title}"

        return {
            'type': 'email',
            'content': content_text,
            'url': None,
            'description': source_description,
            'api_src': api_src
        }

    return None
