import csv

import pandas as pd

if __name__ == '__main__':
    file = pd.read_csv('User_info.csv')
    df = pd.DataFrame(file)

    with open('four.csv', 'w', newline='', encoding='utf_8_sig') as csvfile:
        field = ['user_id','user_name','user_url']
        writer = csv.DictWriter(csvfile, fieldnames=field)
        writer.writeheader()

        for i in range(len(df)):
            document = df[i:i + 1]
            user_url = document['user_url'][i]
            user_id = document['user_id'][i]
            user_name = document['user_name'][i]
            if user_id >= 10000 :
                break
            if user_id >=1000:
                writer.writerow({'user_id': user_id, 'user_name': user_name, 'user_url': user_url})
