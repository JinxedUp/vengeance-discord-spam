import aiohttp
import asyncio
import os
import shutil
import logging
from colorama import Fore, Style, init
from aiofiles.os import stat as aio_stat
from aiofiles import open as aio_open

init(autoreset=True)

logging.basicConfig(filename='spammer.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

ASCII_ART = """
‎
██╗   ██╗███████╗███╗   ██╗ ██████╗ ███████╗ █████╗ ███╗   ██╗ ██████╗███████╗
██║   ██║██╔════╝████╗  ██║██╔════╝ ██╔════╝██╔══██╗████╗  ██║██╔════╝██╔════╝
██║   ██║█████╗  ██╔██╗ ██║██║  ███╗█████╗  ███████║██╔██╗ ██║██║     █████╗
╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██╔══╝  ██╔══██║██║╚██╗██║██║     ██╔══╝
 ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝███████╗██║  ██║██║ ╚████║╚██████╗███████╗
  ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
  Made by Jinx
"""

async def send_message(session, user_token, channel_id, message):
    headers = {
        'Authorization': user_token,
        'Content-Type': 'application/json'
    }
    payload = {'content': message}
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'

    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                logging.info(f"Message sent successfully from token: {user_token}")
                return True
            elif response.status == 429:
                retry_after = (await response.json()).get('retry_after', 1)
                logging.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                await asyncio.sleep(retry_after)
                return await send_message(session, user_token, channel_id, message)
            else:
                logging.error(f"Failed to send message from token: {user_token}. Status code: {response.status}")
                return False
    except aiohttp.ClientError as e:
        logging.error(f"Client error: {e}")
        await asyncio.sleep(10)
        return await send_message(session, user_token, channel_id, message)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await asyncio.sleep(10)
        return await send_message(session, user_token, channel_id, message)

async def spam_messages(user_tokens, channel_id, message, delay):
    total_messages_sent = 0
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [send_message(session, token, channel_id, message) for token in user_tokens]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                total_messages_sent += sum(1 for result in results if result is True)
                print(f"{Fore.MAGENTA}Messages sent: {total_messages_sent}", end='\r')
                await asyncio.sleep(delay)
    except Exception as e:
        logging.critical(f"Critical error in spam_messages: {e}")
        await asyncio.sleep(10)
        await spam_messages(user_tokens, channel_id, message, delay)
    finally:
        print(f"\n{Fore.MAGENTA}Final messages sent: {total_messages_sent}")

async def watch_text_file():
    message = ""
    while True:
        try:
            st = await aio_stat('text.txt')
            modified_time = st.st_mtime
            await asyncio.sleep(1)
            st = await aio_stat('text.txt')
            if st.st_mtime != modified_time:
                print(f"{Fore.MAGENTA}text.txt has been modified. Updating message...{Style.RESET_ALL}")
                await asyncio.sleep(1)
                async with aio_open('text.txt', mode='r') as f:
                    message = await f.read().strip()
        except Exception as e:
            logging.error(f'Error in watch_text_file: {e}')
        await asyncio.sleep(1)
    return message

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    options = f"""
{Fore.MAGENTA}╔═══                              ═══╗
({Fore.YELLOW}1{Fore.MAGENTA}) > Default Spammer
({Fore.YELLOW}2{Fore.MAGENTA}) > Token Select Spammer
({Fore.YELLOW}3{Fore.MAGENTA}) > Token Based Spammer
({Fore.YELLOW}4{Fore.MAGENTA}) > Webhook Spammer
          ({Fore.YELLOW}5{Fore.MAGENTA}) > Custom Text Spammer
               ({Fore.YELLOW}6{Fore.MAGENTA}) > Token Checker (Best)
{Fore.MAGENTA}╚═══                              ═══╝
"""
    return centered_text(ASCII_ART) + centered_text(options)

def centered_text(text, color=Fore.MAGENTA):
    terminal_size = shutil.get_terminal_size((80, 20))
    terminal_width = terminal_size.columns
    lines = text.strip().split('\n')
    centered_lines = [line.center(terminal_width) for line in lines]
    centered_text = '\n'.join(centered_lines)
    return color + centered_text + Style.RESET_ALL

def get_input(prompt):
    return input(Fore.MAGENTA + prompt + Style.RESET_ALL).strip()

async def start_spammer():
    while True:
        try:
            with open('tokens.txt', 'r') as f:
                tokens = f.read().strip().split('\n')

            with open('text.txt', 'r') as f:
                message = f.read().strip()

            channel_id = get_input('Enter the channel ID where you want to send the message: ')
            delay = float(get_input('Enter delay in seconds between rounds of messages (e.g., 5): '))

            clear_screen()
            print(print_menu())
            print(f"{Fore.MAGENTA}Starting Default Spammer...")

            await spam_messages(tokens, channel_id, message, delay)
        except FileNotFoundError:
            print(Fore.RED + 'tokens.txt or text.txt not found. Please create these files with appropriate content.' + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + 'Invalid input.' + Style.RESET_ALL)
        except Exception as e:
            logging.error(f'Error in start_spammer: {e}')
        await asyncio.sleep(5)

async def token_select_spammer():
    while True:
        try:
            with open('tokens.txt', 'r') as f:
                tokens = f.read().strip().split('\n')

            with open('text.txt', 'r') as f:
                message = f.read().strip()

            clear_screen()
            print(print_menu())
            print(f"{Fore.MAGENTA}Select Token to Start Spamming:")
            for idx, token in enumerate(tokens, 1):
                print(f"  ({idx}) {token}")

            choice = int(get_input('Enter the number of the token to start spamming: '))
            if 1 <= choice <= len(tokens):
                token_to_spam = tokens[choice - 1]
                channel_id = get_input('Enter the channel ID where you want to send the message: ')
                delay = float(get_input('Enter delay in seconds between rounds of messages (e.g., 5): '))

                clear_screen()
                print(print_menu())
                print(f"{Fore.MAGENTA}Starting Token Select Spammer for Token: {token_to_spam}...")

                await spam_messages([token_to_spam], channel_id, message, delay)
            else:
                print(Fore.RED + 'Invalid choice. Please select a valid token number.' + Style.RESET_ALL)
        except FileNotFoundError:
            print(Fore.RED + 'tokens.txt or text.txt not found. Please create these files with appropriate content.' + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + 'Invalid input.' + Style.RESET_ALL)
        except Exception as e:
            logging.error(f'Error in token_select_spammer: {e}')
        await asyncio.sleep(5)

async def token_based_spammer():
    try:
        with open('tokens.txt', 'r') as f:
            tokens = f.read().strip().split('\n')

        with open('text.txt', 'r') as f:
            message = f.read().strip()

        channel_id = get_input('Enter the channel ID where you want to send the message: ')
        delay = float(get_input('Enter delay in seconds between rounds of messages (e.g., 5): '))

        clear_screen()
        print(print_menu())
        print(f"{Fore.MAGENTA}Starting Token Based Spammer...")

        async with aiohttp.ClientSession() as session:
            while True:
                for token in tokens:
                    await send_message(session, token, channel_id, message)
                    await asyncio.sleep(delay)
    except FileNotFoundError:
        print(Fore.RED + 'tokens.txt or text.txt not found. Please create these files with appropriate content.' + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + 'Invalid input.' + Style.RESET_ALL)
    except Exception as e:
        logging.error(f'Error in token_based_spammer: {e}')
    await asyncio.sleep(1)

async def webhook_spammer():
    try:
        webhook_url = get_input('Enter the webhook URL where you want to send the message: ')

        with open('text.txt', 'r') as f:
            message = f.read().strip()

        delay = float(get_input('Enter delay in seconds between rounds of messages (e.g., 5): '))

        clear_screen()
        print(print_menu())
        print(f"{Fore.MAGENTA}Starting Webhook Spammer...")

        async with aiohttp.ClientSession() as session:
            while True:
                payload = {'content': message}
                try:
                    async with session.post(webhook_url, json=payload) as response:
                        if response.status == 200:
                            logging.info(f"Message sent successfully to webhook.")
                        else:
                            logging.error(f"Failed to send message to webhook. Status code: {response.status}")
                except aiohttp.ClientError as e:
                    logging.error(f"Client error: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                await asyncio.sleep(delay)
    except FileNotFoundError:
        print(Fore.RED + 'text.txt not found. Please create this file with appropriate content.' + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + 'Invalid input.' + Style.RESET_ALL)
    except Exception as e:
        logging.error(f'Error in webhook_spammer: {e}')
    await asyncio.sleep(2)

async def custom_text_spammer():
    while True:
        try:
            with open('tokens.txt', 'r') as f:
                tokens = f.read().strip().split('\n')

            message = get_input('Enter the custom message you want to spam: ')
            channel_id = get_input('Enter the channel ID where you want to send the message: ')
            delay = float(get_input('Enter delay in seconds between rounds of messages (e.g., 5): '))

            clear_screen()
            print(print_menu())
            print(f"{Fore.MAGENTA}Starting Custom Text Spammer...")

            await spam_messages(tokens, channel_id, message, delay)
        except FileNotFoundError:
            print(Fore.RED + 'tokens.txt not found. Please create this file with appropriate content.' + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + 'Invalid input.' + Style.RESET_ALL)
        except Exception as e:
            logging.error(f'Error in custom_text_spammer: {e}')
        await asyncio.sleep(5)

async def token_checker():
    valid_tokens_count = 0
    invalid_tokens_count = 0

    try:
        with open('tokens.txt', 'r') as f:
            tokens = f.read().strip().split('\n')

        clear_screen()
        print(print_menu())
        print(f"{Fore.MAGENTA}Starting Token Checker...")

        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(10)
            tasks = []

            async def check_token(token):
                nonlocal valid_tokens_count, invalid_tokens_count

                headers = {
                    'Authorization': token,
                    'Content-Type': 'application/json'
                }
                url = 'https://discord.com/api/v9/users/@me'
                masked_token = token[:5] + '*****'
                async with semaphore:
                    try:
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                username = data.get('username', 'Unknown')
                                print(f"{Fore.GREEN}[+] Token is valid: {masked_token} | Identified token as {username}{Style.RESET_ALL}")
                                logging.info(f"[+] Token is valid: {masked_token} | Identified token as {username}")
                                valid_tokens_count += 1
                            else:
                                print(f"{Fore.RED}[-] Token is invalid: {masked_token}{Style.RESET_ALL}. Status code: {response.status}")
                                logging.error(f"[-] Token is invalid: {masked_token}. Status code: {response.status}")
                                invalid_tokens_count += 1
                    except aiohttp.ClientError as e:
                        print(f"{Fore.RED}[-] Client error: {e}{Style.RESET_ALL}")
                        logging.error(f"[-] Client error: {e}")
                        invalid_tokens_count += 1
                    except Exception as e:
                        print(f"{Fore.RED}[-] Unexpected error: {e}{Style.RESET_ALL}")
                        logging.error(f"[-] Unexpected error: {e}")
                        invalid_tokens_count += 1

            for token in tokens:
                tasks.append(check_token(token))

            await asyncio.gather(*tasks)

    except FileNotFoundError:
        print(Fore.RED + 'tokens.txt not found. Please create this file with appropriate content.' + Style.RESET_ALL)
    except Exception as e:
        logging.error(f'Error in token_checker: {e}')

    print(f"{Fore.GREEN}| valid tokens: {valid_tokens_count} {Style.RESET_ALL}| {Fore.RED}invalid tokens: {invalid_tokens_count} {Style.RESET_ALL}")

    await asyncio.sleep(5)


async def main():
    try:
        asyncio.create_task(watch_text_file())
        while True:
            clear_screen()
            print(print_menu())
            choice = get_input('Enter your choice (1-6): ')

            if choice == '1':
                await start_spammer()
            elif choice == '2':
                await token_select_spammer()
            elif choice == '3':
                await token_based_spammer()
            elif choice == '4':
                await webhook_spammer()
            elif choice == '5':
                await custom_text_spammer()
            elif choice == '6':
                await token_checker()
            elif choice.lower() == '0':
                break
            else:
                print(Fore.RED + 'Invalid choice. Please enter a number from 1 to 6.' + Style.RESET_ALL)
    except KeyboardInterrupt:
        print("\n\n")
        print(f"{Fore.MAGENTA}Exiting...{Style.RESET_ALL}")
    except Exception as e:
        logging.critical(f'Critical error in main: {e}')

if __name__ == "__main__":
    try:
        print("Made by Jinx.")

        asyncio.run(main())
    except Exception as e:
        logging.critical(f'Critical error in main: {e}')
