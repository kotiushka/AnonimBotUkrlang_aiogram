import sqlite3


class Database:
    def __init__(self, dbname):
        self.connection = sqlite3.connect(dbname, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def add_queue(self, user_info):
        with self.connection:
            return self.cursor.execute(f"INSERT INTO `rooms` (`chat_id`,`gender`,`gender_search`,`age`,`age_search`,`country`,`country_search`,`city`,`city_search`) VALUES (?,?,?,?,?,?,?,?,?)", (user_info[0],user_info[1],user_info[6],user_info[2], user_info[7],user_info[3], user_info[8],user_info[4], user_info[9]))

    def get_gender_search(self,message):
        gender_search = self.cursor.execute('SELECT `gender_search` FROM `users` WHERE id = ?',(message,)).fetchmany(1)
        return gender_search[0][0]

    def delete_queue(self, chat_id):
        with self.connection:
            return self.cursor.execute(f"DELETE FROM `rooms` WHERE chat_id={chat_id}")

    def delete_chat(self, id_chat):
        with self.connection:
            return self.cursor.execute(f"DELETE FROM `chats` WHERE `id` = ?", (id_chat,))

    def get_chat(self):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `rooms`", ()).fetchmany(1)
            if bool(len(chat)):
                for row in chat:
                    user_info = [row[1], row[2]]
                return user_info
            else:
                return [0]

    def set_active(self,user_id,active):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `active` = ? WHERE id = ?",(active,user_id,))

    def get_user(self):
        with self.connection:
            return self.cursor.execute("SELECT `id`,`active` FROM `users`").fetchall()


    def get_user(self, chat_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM `users` WHERE `id` = ?", (chat_id,)).fetchmany(1)
            if bool(len(user)):
                return user[0]
            else:
                return False


    def get_send(self):
        with self.connection:
            while True:
                text = self.cursor.execute("SELECT `send_text1`,`send_time1` FROM `sendes`").fetchmany(1)
                return text


    def get_info_search(self,message):
        with self.connection:
            my_search_info = self.cursor.execute('SELECT * FROM `users` WHERE `id` = ?', (message,)).fetchmany(1)
            my_gender_search = my_search_info[0][6]
            my_country_search1 = my_search_info[0][8]
            my_city_search = my_search_info[0][9]
            my_age_search = my_search_info[0][7]
            my_gender = my_search_info[0][1]
            my_age = my_search_info[0][2]
            my_country = my_search_info[0][3]
            my_city = my_search_info[0][4]
            if (my_age_search == 'Случайный'):
                first_age = 1
                second_age = 1000
            else:
                first_age = my_age_search.split("-")[0]
                second_age = my_age_search.split("-")[1]

            chat = []
            chats = self.cursor.execute("SELECT * FROM rooms").fetchall()
            for temp in chats:
                my_country_search = my_country_search1
                if ((my_gender_search == temp[2] or my_gender_search == "Случайный") and (
                        int(first_age) <= temp[3] <= int(second_age)) and (
                        my_city_search == temp[5] or my_city_search == "Случайный")
                        and (my_gender == temp[6] or temp[6] == 'Случайный') and (
                                my_city == temp[9] or temp[9] == 'Случайный')):
                    if (temp[7] == 'Случайный'):
                        if (temp[8] == 'Случайный'):
                            if (my_country_search == 'Случайный'):
                                chat.append(temp[1])
                            else:
                                my_country_search = my_country_search.split(", ")
                                if temp[4] in my_country_search:
                                    chat.append(temp[1])
                        else:
                            country_search = temp[8].split(", ")
                            if my_country in country_search:
                                if (my_country_search == 'Случайный'):
                                    chat.append(temp[1])
                                else:
                                    my_country_search = my_country_search.split(", ")
                                    if temp[4] in my_country_search:
                                        chat.append(temp[1])
                    else:
                        first_age_search = int(temp[7].split("-")[0])
                        second_age_search = int(temp[7].split("-")[1])
                        if (first_age_search <= my_age <= second_age_search):
                            if (temp[8] == 'Случайный'):
                                if (my_country_search == 'Случайный'):
                                    chat.append(temp[1])
                                else:
                                    my_country_search = my_country_search.split(", ")
                                    if temp[4] in my_country_search:
                                        chat.append(temp[1])
                            else:
                                country_search = temp[8].split(", ")
                                if my_country in country_search:
                                    if (my_country_search == 'Случайный'):
                                        chat.append(temp[1])
                                    else:
                                        my_country_search = my_country_search.split(", ")
                                        if temp[4] in my_country_search:
                                            chat.append(temp[1])

            if bool(len(chat)):
                user_info = chat
                return user_info
            else:
                return [0]



    def create_chat(self, chat_one, chat_two):
        with self.connection:
            if chat_two != 0:
                # Cоздание чата
                self.cursor.execute(f"DELETE FROM `rooms` WHERE `chat_id` = ?", (chat_two,))
                self.cursor.execute(f"INSERT INTO `chats` (`chat_one`,`chat_two`) VALUES (?,?)", (chat_one, chat_two,))
                return True
            else:
                # Очередь
                return False

    def get_active_chat(self, chat_id):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_one`=?", (chat_id,))
            id_chat = 0
            for row in chat:
                id_chat = row[0]
                chat_info = [row[0], row[2]]

            if id_chat == 0:
                chat = self.cursor.execute("SELECT * FROM `chats` WHERE chat_two=?", (chat_id,))
                for row in chat:
                    id_chat = row[0]
                    chat_info = [row[0], row[1]]
                if id_chat == 0:
                    return False
                else:
                    return chat_info
            else:
                return chat_info
