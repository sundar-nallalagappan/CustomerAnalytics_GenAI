       
import pandas as pd
import os
import langdetect
from dataclasses import dataclass
import emoji
import time
from utils import translate_text, generate_summary, find_answers

@dataclass
class config:
    INPUT_FILE_PATH = 'review_extract.csv'
    TRANSLATE_FLAG  = False
    REV1_SUMMARY    = 'summary/review_1_summary.txt'
    REV2_SUMMARY    = 'summary/review_2_summary.txt'
    REV3_SUMMARY    = 'summary/review_3_summary.txt'
    REV4_SUMMARY    = 'summary/review_4_summary.txt'
    REV5_SUMMARY    = 'summary/review_5_summary.txt'
    EMOJI_RANGES = {
                    "Miscellaneous Symbols and Pictographs": (0x1F300, 0x1F5FF),
                    "Emoticons": (0x1F600, 0x1F64F),
                    "Transport and Map Symbols": (0x1F680, 0x1F6FF),
                    "Alchemical Symbols": (0x1F700, 0x1F77F),
                    "Geometric Shapes Extended": (0x1F780, 0x1F7FF),
                    "Supplemental Arrows-C": (0x1F800, 0x1F8FF),
                    "Supplemental Symbols and Pictographs": (0x1F900, 0x1F9FF),
                    "Chess Symbols": (0x1FA00, 0x1FA6F),
                    "Symbols and Pictographs Extended-A": (0x1FA70, 0x1FAFF),
                    "Miscellaneous Symbols": (0x2600, 0x26FF),
                    "Dingbats": (0x2700, 0x27BF),
                    "Variation Selectors": (0xFE00, 0xFE0F),
                    "Supplemental Symbols and Pictographs": (0x1F900, 0x1FAFF)
                    }
    Q_DICT = {
            'Q1'  : "How would you rate your overall experience using our online application?",
            'Q2'  : "What features do you find most useful or convenient?",
            'Q3'  : "Are there any aspects of the application that you find difficult to use or navigate?",
            'Q4'  : "Are you satisfied with the variety and quality of products available on our platform?",
            'Q5'  : "Have you ever encountered out-of-stock items that you wished were available?",
            'Q6'  : "Is there a specific product or category of products you would like to see added to our inventory?",
            'Q7'  : "How easy is it to place an order on our platform?",
            'Q8'  : "Do you have any suggestions for improving the ordering process?",
            'Q9'  : "How satisfied are you with the delivery times and communication?",
            'Q10' : "Are there any improvements we could make to our delivery or pickup services?",
            'Q11' : "Have you ever needed to contact customer service for assistance? If so, how was your experience?",
            'Q12' : "Are there any additional support features or services you would like to see offered?",
            'Q13' : "Would you recommend our online grocery application to others?",
            'Q14' : "What could we do to improve your overall experience with our platform?"
            }
    
class DataIngestion:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def read_input(self):
        return pd.read_csv(self.file_path)
    
    def impute_emoji(self, text):
        has_emojis = any(any(start <= ord(char) <= end for char in text)
                 for start, end in config.EMOJI_RANGES.values())

        if has_emojis:
            test_without_emoji = emoji.demojize(text)
        else:
            test_without_emoji = text
        return test_without_emoji
    
    def clean_emoji(self, df, col_to_inspect):
        temp = df.copy()
        temp['content_cleaned'] = temp[col_to_inspect].apply(self.impute_emoji)
        return temp
    
    def check_lang(self, text):
        return langdetect.detect(text)
    
    def detect_language(self, df, col_to_inspect):
        df['language'] = df[col_to_inspect].apply(self.check_lang)
        return df
    
    def translate_to_en(self, df):
        temp = df.copy()
        temp['translated_review'] = temp.apply(lambda row: translate_text(row['content_cleaned'], row['language']) if row['language'] != 'en' else row['content_cleaned'], axis=1)
        return temp
    
    def combine_star_reviews(self, df, rating_col, col_to_check):
        review_1_star = ''
        review_2_star = ''
        review_3_star = ''
        review_4_star = ''
        review_5_star = ''

        for i in sorted(df[rating_col].unique()):
            comb_rev = ''
            comb_rev = "\n".join(df[df[rating_col] == i][col_to_check])
            
            if i == 1:
                review_1_star = comb_rev
            elif i == 2:
                review_2_star = comb_rev
            elif i == 3:
                review_3_star = comb_rev
            elif i == 4:
                review_4_star = comb_rev
            elif i == 5:
                review_5_star = comb_rev
                
        print(f'review_1_star: {len(review_1_star)} | review_2_star: {len(review_2_star)} | review_3_star: {len(review_3_star)} | review_4_star: {len(review_4_star)} | review_5_star: {len(review_5_star)}')        
        print('review_1_star:', review_1_star[0:100])
        print('review_5_star:', review_5_star[0:100])
        return review_1_star, review_2_star, review_3_star, review_4_star, review_5_star    
    
    def generate_summary(self, review, max_tokens) :
        summary = generate_summary(review, max_tokens)
        return summary

    def store_summary(self, summary, out_path):
        with open(out_path, "w") as file:
            file.write(summary)
            
    def get_insights(self, review):
        qanda = {}
        for key in config.Q_DICT.keys():
            print(f"Question {key} in progress")
            response = find_answers(review, config.Q_DICT[key])
            qanda[config.Q_DICT[key]] = response
            time.sleep(20)
        return qanda
    
    def store_qanda(self, qanda):
        temp = pd.DataFrame(list(qanda.items()), index=range(len(qanda)), columns=['Question', 'Insights'])
        temp.to_csv("QandA.csv", index=False, header=True)
        

if __name__ == '__main__':
    print("sairam")
    dataingestion = DataIngestion(config.INPUT_FILE_PATH)
    review_data   = dataingestion.read_input()
    review_data_cleaned = dataingestion.clean_emoji(review_data, 'content')
    review_data_cleaned   = dataingestion.detect_language(review_data_cleaned, 'content_cleaned')
    
    config.TRANSLATE_FLAG = False
    if config.TRANSLATE_FLAG:
        review_data_translated = dataingestion.translate_to_en(review_data_cleaned)
        review_data_translated.to_csv('review_data_translated.csv')
    else:
        review_data_translated = pd.read_csv('review_data_translated.csv')
        
    
    review_1_star, review_2_star, review_3_star, review_4_star, review_5_star = dataingestion.combine_star_reviews(review_data_translated, 'score', 'translated_review')
    
    
    review_1_summary = dataingestion.generate_summary(review_1_star,200)
    review_2_summary = dataingestion.generate_summary(review_2_star,200)
    review_3_summary = dataingestion.generate_summary(review_3_star,300)
    review_4_summary = dataingestion.generate_summary(review_4_star,200)
    review_5_summary = dataingestion.generate_summary(review_5_star[0:75000], 200)
    
    dataingestion.store_summary(review_1_summary, config.REV1_SUMMARY)
    dataingestion.store_summary(review_2_summary, config.REV2_SUMMARY)
    dataingestion.store_summary(review_3_summary, config.REV3_SUMMARY)
    dataingestion.store_summary(review_4_summary, config.REV4_SUMMARY)
    dataingestion.store_summary(review_5_summary, config.REV5_SUMMARY)
    
    rev3_rev4 = review_4_star + '\n' + review_3_star + '\n' 
    qanda = dataingestion.get_insights(rev3_rev4)
    dataingestion.store_qanda(qanda)