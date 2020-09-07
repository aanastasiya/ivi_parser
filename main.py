from bs4 import BeautifulSoup
import requests


def save_file(data):
    with open('movies.csv', 'w') as f:
        for key in data.keys():
            f.write("%s;%s\n" % (key, data[key]))


def get_data():
    url = 'https://www.ivi.ru'
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    categories = []
    # Ищет ссылки на каждый из разделов каталога
    for a in soup.find('ul', class_='top-menu__sublist').find_all('a'):
        categories.append(url + a['href'])

    data = {}
    # Обходит страницы в одном разделе
    for category in categories:
        soup = BeautifulSoup(requests.get(category).text, 'lxml')
        # В soup-e находились не все теги со ссылками на следующие страницы, но всегда была последняя,
        # поэтому дальше находится номер последней страницы и начинается цикл по ним
        pages = int(max([page.text for page in soup.find_all('div', class_='nbl-option__caption')]))
        for num in range(1, pages):
            response = requests.get('{category}/page{num}'.format(category=category, num=num))
            soup = BeautifulSoup(response.text, 'lxml')

            # Обходит все найденные фильмы и ищет разделы, относящиеся к ним
            for li in soup.find_all('li', class_='gallery__item gallery__item_virtual'):
                try:
                    title = li.find('div', class_='nbl-slimPosterBlock__title').text
                    if title not in data.keys():
                        print(title)
                        data[title] = get_tags(url + li.a['href'])
                except AttributeError:
                    pass

    print(len(data))
    save_file(data)


# Собирает разделы, к которым относится фильм
def get_tags(link):
    soup = BeautifulSoup(requests.get(link).text, 'lxml')
    tags = []
    try:
        for a in soup.find('div', class_='parameters__info').find_all('a'):
            tags.append(a.text)
    except AttributeError:
        pass
    return ','.join(tags)


if __name__ == '__main__':
    get_data()
