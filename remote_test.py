from PIL import Image

from tesserocr import PyTessBaseAPI, image_to_text

from generic_helpers.get_unix_time import get_unix_time
image_open = Image.open('./image_flask.png')
# start = get_unix_time()
# for i in range(0, 100):
#     image_to_string(image_open)
#     # tmp = api.GetUTF8Text()
# end = get_unix_time()
# diff = end - start
# print(diff)

start = get_unix_time()

with PyTessBaseAPI(path="/FAST_DATA/tessdata_fast/") as api:
    for i in range(0, 100):
        api.SetImage(image_open)
        api.GetUTF8Text()
end = get_unix_time()
diff = end - start
print(diff)

# start = get_unix_time()
# image_open = Image.open('./image_flask.png')
# for i in range(0, 100):
#     image_to_text(image_open)
#     # tmp = api.GetUTF8Text()
# end = get_unix_time()
# diff = end - start
# print(diff)
