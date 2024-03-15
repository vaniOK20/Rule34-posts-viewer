import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import random
from PIL import Image, ImageTk
from io import BytesIO

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
num = 0
tags_img = ""
sr = ""
images=[]
is_backed=False

def print_html(url):
	headers = {'User-Agent': USER_AGENT}
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
	except requests.RequestException as e:
		print(f"Error fetching URL: {e}")
		return None
	return response.text

def extract_text_after_keyword(text, keyword):
	index = text.find(keyword)
	return text[index + len(keyword):].strip() if index != -1 else "Keyword not found in the text."

def search(url, tags):
	global images, num, tags_img

	html_content = print_html(url)
	if not html_content:
		print("Failed to fetch initial page.")
		return None

	result = extract_text_after_keyword(html_content, '<div class="image-list">')
	soup = BeautifulSoup(result, 'html.parser')
	span_tags = soup.find_all('span')

	if not span_tags:
		print("No <span> tags found. Retrying search.")
		text = find_last_page(f'https://rule34.xxx/index.php?page=post&s=list&tags={tags}')
		num = num + 1
		return search(f'https://rule34.xxx/index.php?page=post&s=list&tags={tags}&pid={random.randint(-3, int(text)-num)}', tags)

	random_span = random.choice(span_tags)

	while not 'class="thumb"' in str(random_span):
		random_span = random.choice(span_tags)
		print('while')

	a_tag = random_span.find('a')

	if not a_tag:
		print("No <a> tag found in random <span>. Retrying search.")
		text = find_last_page(f'https://rule34.xxx/index.php?page=post&s=list&tags={tags}')
		num = num + 1
		return search(f'https://rule34.xxx/index.php?page=post&s=list&tags={tags}&pid={random.randint(-3, int(text)-num)}', tags)

	value = a_tag.text
	link = a_tag['href']
	img_t = a_tag.find('img')
	if img_t:
		tags_img = img_t['alt'] + '####_https://rule34.xxx' + link + '_####'

	image_page_content = print_html("https://rule34.xxx" + link)

	if not image_page_content:
		print("Failed to fetch image page.")
		return None

	soup = BeautifulSoup(image_page_content, 'html.parser')
	img_tag = soup.find('img', id='image')

	if not img_tag:
		img_tag = soup.find('video', id='gelcomVideoPlayer')
		if img_tag:
			video_tag = img_tag.find('source')
			src = video_tag['src']
			print("Sorry but python tkinter not have video player. Video source:")
			print(src)
			src = img_tag['poster']
			num = 0
			return src
		else:
			print("Image tag not found.")
			return None

	src = img_tag['src']
	num = 0

	if src[src.find('?')+1:] in images:
		print('src in images')
		return search(f'https://rule34.xxx/index.php?page=post&s=list&tags={tags}&pid={random.randint(-3, int(text)-num)}', tags)

	if not len(images)==0:
		images.append(src[src.find('?')+1:])
	else:
		images=[src[src.find('?')+1:]]
	return src

def update_image(url):
	headers = {'User-Agent': USER_AGENT, 'Referer': 'https://rule34.xxx/'}
	try:
		response = requests.get(url, headers=headers)
		if response.ok:
			image_data = response.content
			if image_data:
				image = Image.open(BytesIO(image_data))
				image = image.resize((384, 384), Image.BICUBIC)
				photo = ImageTk.PhotoImage(image)
				fotoD.config(image=photo)
				fotoD.image = photo
				photo0 = photo
			else:
				print("Failed to load image data.")
		else:
			print(f"Failed to fetch image from URL. HTTP Error: {response.status_code}")
	except requests.RequestException as e:
		print(f"Error fetching image from URL: {e}")

def down():
	global sr
	if sr:
		headers = {'User-Agent': USER_AGENT, 'Referer': 'https://rule34.xxx/'}
		try:
			response = requests.get(sr, headers=headers)
			if response.ok:
				image_data = response.content
				if image_data:
					with open(f"{random.randint(0, 100000)}.jpg", "wb") as file:
						file.write(image_data)
				else:
					print("Failed to load image data.")
			else:
				print(f"Failed to fetch image from URL. HTTP Error: {response.status_code}")
		except requests.RequestException as e:
			print(f"Error fetching image from URL: {e}")
	else:
		print("No image to download.")

def conf(tags):
	global sr, num, is_backed, text
	if is_backed==False:
		tags = tags.replace(" ", "+")
		text = find_last_page(f'https://rule34.xxx/index.php?page=post&s=list&tags={tags}')
		if text is not None:
			sr = search(f'https://rule34.xxx/index.php?page=post&s=list&tags={tags}&pid={random.randint(-3, int(text)-num)}', tags)
			if sr:
				update_image(sr)
				num = 0
			else:
				print("No image found.")
				window.after(6000, lambda: conf(tags))
				num = num + 1
		else:
			print("Failed to find last page.")
	else:
		tags_s(f'https://rule34.xxx/index.php?page=history&type=tag_history&id={images[len(images)-2]}')
		is_backed=False
		update_image(sr)

def tags_f():
	messagebox.showinfo("Tags", tags_img.replace(" ", "    "))
	print(tags_img)

def find_last_page(url):
	html_content = print_html(url)
	Last_page = extract_text_after_keyword(html_content, '<div class="pagination">')
	soup2 = BeautifulSoup(Last_page, 'html.parser')
	a_tags = soup2.find_all('a')
	a_tag_last_page = soup2.find('a', alt="last page")
	if a_tag_last_page is None:
		if len(a_tags)<=1:
			return 0
		print("idk")
		return 1564
	text = a_tag_last_page['href']
	index = text.find('pid=')
	if not int(text[index+4:])>=8475726:
		return text[index+4:]
	else:
		return 1564

def back():
	global is_backed
	if len(images)>=1:
		link=f'https://rule34.xxx/index.php?page=post&s=view&id={images[len(images)-2]}'
		soup = find_(link)
		img_tag = soup.find('img', id='image')
		src = img_tag['src']
		tags_s(f'https://rule34.xxx/index.php?page=history&type=tag_history&id={images[len(images)-2]}')
		if src:
			is_backed=True
			update_image(src)
		else:
			print('error')
	else:
		print('error')

def find_(link):
	image_page_content = print_html(link)
	soup = BeautifulSoup(image_page_content, 'html.parser')
	return soup

def tags_s(url):
	global tags_img
	soup2 = find_(url)
	tr = soup2.find('tr', id="r4")
	if tr is None:
		print("tr is None")
		tr = soup2.find('tr', id="r3")
		if tr is None:
			tr = soup2.find('tr', id="r2")
	spans = tr.find_all('span', class_="unchanged-tags")
	spans2 = [a.get_text() for span in spans for a in span.find_all('a')]
	tags_img=str(spans2).replace(',', ' ').replace("'", "").replace('[', '').replace(']', ' ')+'####_https://rule34.xxx' + url + '_####'

window = tk.Tk()
window.geometry("390x415")
s = tk.StringVar()

fotoD = tk.Label(window)
fotoD.pack()

entry = tk.Entry(window, textvariable=s)
confirm = tk.Button(window, text="Find", command=lambda: conf(s.get()))
download = tk.Button(window, text="Download", command=down)
tegs = tk.Button(window, text="See tags", command=tags_f)
back = tk.Button(window, text="Back", command=back)

entry.pack(side=tk.LEFT, pady=2, padx=1)
confirm.pack(side=tk.LEFT)
download.pack(side=tk.LEFT)
tegs.pack(side=tk.LEFT)
back.pack(side=tk.LEFT)

conf('random')
window.mainloop()
