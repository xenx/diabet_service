import speechkit
from speechkit import log
import urllib.request
import urllib.parse
import pyaudio  
import wave
import re
import pymongo
import datetime
from pymongo import MongoClient
import config

error_message = "Я не расслышала, повторите пожалуйста"

def generateDigits(text):
	digits = re.split("\D+", text)
	result = str(digits[0])
	result_digital = result
	if len(digits) > 1:
		result += " целых и " + str(digits[1]) + " десятых"
		result_digital += "." + str(digits[1])
	return (float(result_digital), result + " миллимоль на литр")

def saveSugarValueToMongo(sugar_value):
	client = MongoClient(config.mongo_connection)
	db = client.diabetlab
	collection = db.results
	time_now = str(datetime.datetime.utcnow())
	time_now = time_now[:time_now.find(".")]
	post = {
		"type": "GL",
		"value": sugar_value,
		"time": time_now,
		"user_id": "58b090473bd4f4188b200616"
	}
	log("Значение сахара " + str(sugar_value) + " сохранено с id " + str(collection.insert_one(post).inserted_id))


def main():
	speechkit.tts("Вы измеряли сахар сегодня?")
	answer = speechkit.record_to_text_looped(error_message)
	if ("да" in answer):
		speechkit.tts("И сколько у вас получилось?")
		while True:
			sugar_value = speechkit.record_to_text_looped(error_message)
			float_digits, string_digits = generateDigits(sugar_value)
			speechkit.tts(string_digits + ", правильно?")
			answer = speechkit.record_to_text_looped(error_message)
			if ("не" in answer):
				speechkit.tts("Тогда повторите еще раз, пожалуйста")
			elif ("да" in answer):
				speechkit.tts("Спасибо, ваши данные сохранены. До свидания")
				saveSugarValueToMongo(float_digits)
				break
			else:
				speechkit.tts(error_message)

if __name__ == "__main__":
	main()