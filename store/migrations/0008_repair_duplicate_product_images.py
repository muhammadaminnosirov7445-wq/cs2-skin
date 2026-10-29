from django.db import migrations


OLD_DUPLICATE_URL = (
    'https://community.akamai.steamstatic.com/economy/image/'
    'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL1m5fn8Sdk'
    '7vORbqhsLfWAMWuZxuZi_uI_TX6wxxkjsGXXnImsJ37COlUoWcByEOMOtxa5kdXmNu3htVPZjN1bjXKpkHLRfQU'
)

UNIQUE_IMAGES = {
    '★ Karambit | Doppler': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1Q7uCvZaZkNM-SA1iSze91u_FsTju_qhAmoT-Jn4bjJC_4Ml93UtZuRLQPsBawkNfiMbnl5AKMiopCnin7iCJBv31j4rkBBKEg-6zUjV3GY6p9v8dpLWT3Fg'
    ),
    'AWP | Atheris': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwiYbf-jFk7uW-V617LfmBGDidxOp_pewnF3njyUl0sWqSzN39eCiUPQR2DpUlQeRftBe4wd7uNr_n41HYidkUzSv42S9I6is7tuoCBKUh-KjWkUdS'
    ),
    'AK-47 | Frontside Misty': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwlcK3wiFO0POlV6F-Ju6EDW-Ez-975bZkSju_rBlw5z-DyN-td3zBPA5xWZl0ROALtkG_x9LnM-7m4FfbjdoXyyvy2HgcuDE9t7QHU7hLpKXb5H_xWw'
    ),
    'AK-47 | Uncharted': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwlcK3wiFO0POlV6Z-K_CcD36fzeJpvu1uSzy1rBki42aDzo2tdn_FaFIiW8VyEe4K50blwt_mMbnm5FWM3otAnS73238XuSU64rI'
    ),
    'M4A4 | Magnesium': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL8ypexwjFS4_GqZ6R-JeLDCmGezupmte4mFjqhxEt0sDuGzoyvciiUPQR2C5d1QOBYshftkdDkZu_n5Vbfid9Dzyv5hywYuH1r4bU'
    ),
    'Desert Eagle | Blaze': OLD_DUPLICATE_URL,
    'Glock-18 | Water Elemental': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL2kpnj9h1a7s29a6h4L_yaCHGFzeRkse1VQyCxnk5psDuGzIypeCiUPQR2Cpd0ROBbtBfsxYDmZu3mtFSO34xHzyn4hi9K5Sg0k7s'
    ),
    'P250 | Valence': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwmYbm7S9A4_uqe6R_JeLDC2GDzupk5bVqSCG_qkhpsTqCn43hI3vBbwchC5tyEe4K50blwt_mMbnm5FWM3otAnS73238XuSU64rI'
    ),
    'Desert Eagle | Corinthian': (
        'https://community.akamai.steamstatic.com/economy/image/'
        'i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL1m5fn8Sdk7eOBaKFsJ_CcD3-fzupmsbVtSmDgnAElsDuGyt-pdn_FaFIiW8VyEe4K50blwt_mMbnm5FWM3otAnS73238XuSU64rI'
    ),
}


def repair_images(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for title, image_url in UNIQUE_IMAGES.items():
        Product.objects.filter(title=title, image_url=OLD_DUPLICATE_URL).update(image_url=image_url)


def restore_duplicate_images(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for title, image_url in UNIQUE_IMAGES.items():
        Product.objects.filter(title=title, image_url=image_url).update(image_url=OLD_DUPLICATE_URL)


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0007_skinbattle_unique_daily_skin_battle'),
    ]

    operations = [
        migrations.RunPython(repair_images, restore_duplicate_images),
    ]
