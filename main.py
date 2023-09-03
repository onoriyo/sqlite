# ./official-cpe-dictionary_v2.3.xml ファイルを読み込み、cpe：/{種別}：{ベンダ名}：{製品名}：{バージョン}：{アップデート}：{エディション}：{言語}という形式で記録されているCPE情報を、test.sqlite データベースに格納する。

import sqlite3
import xml.etree.ElementTree as ET

# データベースに接続
conn = sqlite3.connect('test.sqlite')
cur = conn.cursor()

# テーブルの作成。{種別}：{ベンダ名}：{製品名}：{バージョン}：{アップデート}：{エディション}：{言語}の、それぞれのtableを作成する。親の要素{種別}は、{ベンダ名}への外部キーとして設定する。
cur.executescript('''
DROP TABLE IF EXISTS CPE;
                  
CREATE TABLE TYPE (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT
);
                  
CREATE TABLE VENDOR (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT
    type_id INTEGER REFERENCES TYPE(id)
);
                  
CREATE TABLE PRODUCT (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT,
    type_id INTEGER REFERENCES TYPE(id),
    vendor_id INTEGER REFERENCES VENDOR(id)
);

CREATE TABLE VERSION (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT,
    type_id INTEGER REFERENCES TYPE(id),
    vendor_id INTEGER REFERENCES VENDOR(id),
    product_id INTEGER REFERENCES PRODUCT(id)
);

CREATE TABLE UD (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT,
    type_id INTEGER REFERENCES TYPE(id),
    vendor_id INTEGER REFERENCES VENDOR(id),
    product_id INTEGER REFERENCES PRODUCT(id),
    version_id INTEGER REFERENCES UD(id)
);

CREATE TABLE EDITION (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT,
    type_id INTEGER REFERENCES TYPE(id),
    vendor_id INTEGER REFERENCES VENDOR(id),
    product_id INTEGER REFERENCES PRODUCT(id),
    version_id INTEGER REFERENCES UD(id)
);

CREATE TABLE LANGUAGE (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT,
    type_id INTEGER REFERENCES TYPE(id),
    vendor_id INTEGER REFERENCES VENDOR(id),
    product_id INTEGER REFERENCES PRODUCT(id),
    version_id INTEGER REFERENCES UD(id)
);
''')
                  
# XMLファイルの読み込み
tree = ET.parse('./official-cpe-dictionary_v2.3.xml')
root = tree.getroot()

# CPE情報の取得。root→<cpe-list>→<cpe-item name="cpe:/a:%240.99_kindle_books_project:%240.99_kindle_books:6::~~~android~~">という形式で記録されている。
for child in root:
    for cpe in child:
        print(child.tag,child.attrib)
        cpe_name = cpe.get('name')
        if cpe_name is not None:
            cpe_type = ''
            cpe_vendor = ''
            cpe_product = ''
            cpe_version = ''
            cpe_ud = ''
            cpe_edition = ''
            cpe_language = ''

            # cpe_nameを「:」で分割し、cpe_type, cpe_vendor, cpe_product, cpe_version, cpe_ud, cpe_edition, cpe_languageに格納する。
            cpe_name = cpe_name.split(':')
            cpe_type = cpe_name[1]
            cpe_vendor = cpe_name[2]
            cpe_product = cpe_name[3]
            cpe_version = cpe_name[4]
            cpe_ud = cpe_name[5]
            cpe_edition = cpe_name[6]
            cpe_language = cpe_name[7]
            cur.execute('''INSERT OR IGNORE INTO CPE (cpe, type, vendor, product, version, ud, edition, language) VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )''', ( cpe_name[0], cpe_type, cpe_vendor, cpe_product, cpe_version, cpe_ud, cpe_edition, cpe_language ) )
            conn.commit()

# データベースの切断
cur.close()
conn.close()
