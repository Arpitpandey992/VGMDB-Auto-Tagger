import codecs

sjis_string = b"01_\x8e\x82\x8f\x97\x82\xcd\x90\x56\x8d\xa1\x82\xb3\x82\xcc"  # Shift JIS encoded bytes
utf8_string = codecs.decode(sjis_string, 'shift_jis')  # Decodes the bytes to UTF-8

print(utf8_string)  # Prints "01_-_Opening.mp3"
