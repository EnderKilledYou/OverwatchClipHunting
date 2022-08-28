def crop(img):
    right = img.width - (img.width * .25)
    left = (img.width * .27)
    upper = img.height / 2
    lower = img.height - (img.height * .18)
    im_crop = img.crop(  # (left, upper, right, lower)-
        (left,
         upper,  # crop the part where it tells you where shit happens.
         right,
         lower)
    )

    return im_crop
