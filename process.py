import re

def get_num_kanji(sentence):
    # Your implementation to count the number of kanji characters in the sentence
    # For example, if using regex:
    kanji_matches = re.findall('[\u4e00-\u9fff々]', sentence)
    return len(kanji_matches)

def katakana_to_hiragana(char):
    # Use re.sub with a custom function to convert Katakana to Hiragana
    return re.sub(r'[\u30a1-\u30f6]', lambda x: chr(ord(x.group()) - 96), char)

def is_kanji_or_kana(char):
    # Use a regular expression to match kanji or kana characters
    return re.match(r'[\u4e00-\u9fff\u3040-\u30ff]', char) is not None

def is_kanji(text):
    # Use a regular expression to check if the text contains any kanji characters
    return bool(re.search('[\u4e00-\u9fff々]', text))

def is_japanese_char(char):
    # Define a regex pattern for Japanese characters
    japanese_pattern = re.compile(r'[\u3040-\u30ff\u4e00-\u9faf\u3400-\u4dbf々]')

    # Check if the character matches the Japanese pattern
    return bool(japanese_pattern.match(char))

def get_jp_text(text):
    jp_text = ''
    for char in text:
        if is_japanese_char(char):
            jp_text += katakana_to_hiragana(char)
    return jp_text

INPUT_JP_EN = 'jp_en_sentences.txt'
INPUT_TRANSCRIPTION = 'jpn_transcriptions.txt'
INPUT_REVIEWS = 'users_sentences.txt'

OUTPUT_FILE = 'processed_sentences.txt'

sentence_data = {}
unique_text = set()

skipped_duplicate = 0
skipped_similarity = 0

skipped_transcript = 0
skipped_reviews = 0
skipped_incomplete = 0

skipped_len = 0
skipped_kj = 0

MIN_LEN, MAX_LEN = 6, 20
MIN_KANJI, MAX_KANJI = 2, 10
MIN_JP_LEN = 6

def get_splits(sen_jp_text):
    splits = []
    half_len = int(len(sen_jp_text) / 2) + 1
    endmark = len(sen_jp_text) - half_len + 1
    for i in range(endmark):
        split = sen_jp_text[i:i+half_len]
        splits += [split]
    return splits

# Process lines in jp_en_sentences.txt
with open(INPUT_JP_EN, 'r', encoding='utf-8') as file_jp_en:
    for line in file_jp_en:
        transcript, review = '', ''
        sent_id, text, en_id, english = line.strip().split('\t')        
        data = [text, transcript, english, review]
        sentence_data[sent_id] = data

# Process lines in jpn_transcriptions.txt
with open(INPUT_TRANSCRIPTION, 'r', encoding='utf-8') as file_transcription:
    for line in file_transcription:
        sent_id, lang, creator, reviewer, transcript = line.strip().split('\t')

        if sent_id in sentence_data:        
            if not reviewer:
                skipped_transcript += 1
                continue

            data = sentence_data[sent_id]
            data[1] = transcript
            sentence_data[sent_id] = data

# Process lines in users_sentences.txt
with open(INPUT_REVIEWS, 'r', encoding='utf-8') as file_reviews:
    for line in file_reviews:
        user, sent_id, review, added, edited = line.strip().split('\t')

        if sent_id in sentence_data:
            if int(review) < 1:  # Fix: Convert review to integer for comparison
                skipped_reviews += 1
                continue

            data = sentence_data[sent_id]
            data[3] = review
            sentence_data[sent_id] = data

sentences = []
total_length = 0
total_kanji = 0

for sent_id, data in sentence_data.items():
    text, transcript, english, review = data

    sen_len = len(text)
    sen_kanji = get_num_kanji(text)

    total_length += sen_len
    total_kanji += sen_kanji

    sen_jp_text = get_jp_text(text)

    if not transcript or not review:
        skipped_incomplete += 1
        continue    

    if not MIN_LEN <= sen_len <= MAX_LEN:
        skipped_len += 1
        continue

    if not MIN_JP_LEN <= len(sen_jp_text):
        skipped_len += 1
        continue

    if not MIN_KANJI <= sen_kanji <= MAX_KANJI:
        skipped_kj += 1
        continue

    if sen_jp_text in unique_text:
        skipped_duplicate += 1
        continue
    else:
        unique_text.add(sen_jp_text)

    sentence = '\t'.join([text, transcript, english, sen_jp_text])
    sentences += [sentence]

sentences = sorted(sentences, key=lambda x: x.split('\t')[0])
sentences = sorted(sentences, key=lambda x: len(x.split('\t')[3]))

average_length = int(total_length / len(sentence_data))
average_kanji = int(total_kanji / len(sentence_data))

output_sentences = []
megatext = ''
for sentence in sentences:
    text, transcript, english, jp_text = sentence.split('\t')

    splits = get_splits(jp_text)
    sentence += '\t' + str(splits)

    found_dup = False
    for split in splits:
        if split in megatext:
            found_dup = True
    
    if found_dup:
        skipped_similarity += 1
        continue

    megatext += ';' + jp_text
    output_sentences += [sentence]

# Write processed data to the output file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as output_file:
    for sentence in output_sentences:
        output_line = sentence + '\n'
        output_file.write(output_line)


print(f'Skipped due to unreviewed transcript: {skipped_transcript}')
print(f'Skipped due to failed review: {skipped_reviews}')
print(f'Skipped due to incomplete: {skipped_incomplete}')
print()
print(f'Average length: {average_length}')
print(f'Average kanji: {average_kanji}')
print()
print(f'Skipped duplicates: {skipped_duplicate}')
print(f'Skipped due to similarity: {skipped_similarity}')
print(f'Skipped due to length: {skipped_len}')
print(f'Skipped due to number of kanji: {skipped_kj}')