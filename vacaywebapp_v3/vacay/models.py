from django.db import models

# Create your models here.

class Employee(models.Model):
    em_id=models.CharField(max_length=11)
    adminID=models.CharField(max_length=11)
    image = models.CharField(max_length=500)
    name = models.CharField(max_length=80)
    gender = models.CharField(max_length=20)
    email = models.CharField(max_length=80)
    password = models.CharField(max_length=30)
    millennial = models.CharField(max_length=20)
    givenbuck = models.CharField(max_length=11)
    usedbuck = models.CharField(max_length=11)
    interaction = models.CharField(max_length=11)
    status = models.CharField(max_length=2)
    company = models.CharField(max_length=50)

class InfoBuffer(models.Model):
    email=models.CharField(max_length=80)
    job=models.CharField(max_length=200)
    survey = models.CharField(max_length=800)

class CommonUser(models.Model):
    userid = models.CharField(max_length=11)
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    email = models.CharField(max_length=80)
    age = models.CharField(max_length=5)
    address = models.CharField(max_length=200)
    job = models.CharField(max_length=300)
    education = models.CharField(max_length=200)
    interests = models.CharField(max_length=2000)
    relationship = models.CharField(max_length=300)
    place_name = models.CharField(max_length=200)
    user_lat = models.CharField(max_length=200)
    user_lon = models.CharField(max_length=200)
    photo_url = models.CharField(max_length=500)
    survey = models.CharField(max_length=5000)
    em_millennial = models.CharField(max_length=50)
    phone_number=models.CharField(max_length=50)


class MailBox(models.Model):
    mail_id = models.CharField(max_length=11)
    from_mail=models.CharField(max_length=100)
    to_mail=models.CharField(max_length=100)
    text_message = models.CharField(max_length=6000)
    image_message_url = models.CharField(max_length=500)
    lat_message = models.CharField(max_length=100)
    lon_message = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    photo_url = models.CharField(max_length=500)
    request_date = models.CharField(max_length=50)
    service = models.CharField(max_length=50)
    service_reqdate=models.CharField(max_length=50)

class EatDrink(models.Model):
    edrink_id = models.CharField(max_length=11)
    photo=models.CharField(max_length=800)
    name=models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    menu = models.CharField(max_length=800)
    opentable = models.CharField(max_length=800)
    location = models.CharField(max_length=800)

class Job(models.Model):
    job_id=models.CharField(max_length=11)
    adminID=models.CharField(max_length=11)
    adminlogo = models.CharField(max_length=500)
    admincompany = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    req = models.CharField(max_length=11)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.CharField(max_length=4000)
    postdate = models.CharField(max_length=30)
    empty = models.CharField(max_length=500)
    survey = models.CharField(max_length=500)
    video = models.CharField(max_length=500)
    youtube = models.CharField(max_length=500)

class Announce(models.Model):
    an_id=models.CharField(max_length=11)
    adminID=models.CharField(max_length=11)
    adminlogo = models.CharField(max_length=500)
    admincompany = models.CharField(max_length=100)
    image = models.CharField(max_length=500)
    title = models.CharField(max_length=300)
    audience = models.CharField(max_length=300)
    subject = models.CharField(max_length=300)
    description = models.CharField(max_length=4000)
    callofaction = models.CharField(max_length=300)
    owneremail = models.CharField(max_length=80)
    viewnum = models.CharField(max_length=11)
    responsenum = models.CharField(max_length=11)
    postdate = models.CharField(max_length=30)
    survey = models.CharField(max_length=500)

class Media(models.Model):
    video = models.CharField(max_length=500)
    youtube = models.CharField(max_length=500)
    imageA = models.CharField(max_length=500)
    imageB = models.CharField(max_length=500)
    imageC = models.CharField(max_length=500)
    imageD = models.CharField(max_length=500)
    imageE = models.CharField(max_length=500)
    imageF = models.CharField(max_length=500)
    descA = models.CharField(max_length=500)
    descB = models.CharField(max_length=500)
    descC = models.CharField(max_length=500)
    descD = models.CharField(max_length=500)
    descE = models.CharField(max_length=500)
    descF = models.CharField(max_length=500)

class Watercooler(models.Model):
    wc_id = models.CharField(max_length=11)
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=80)
    photo=models.CharField(max_length=500)
    company=models.CharField(max_length=30)
    category = models.CharField(max_length=100)
    content = models.CharField(max_length=5000)
    link = models.CharField(max_length=1000)
    whose = models.CharField(max_length=20)

class Comment(models.Model):
    comment_id = models.CharField(max_length=11)
    info_id = models.CharField(max_length=11)
    photoUrl=models.CharField(max_length=500)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=80)
    text = models.CharField(max_length=5000)
    imageUrl = models.CharField(max_length=500)
    whose = models.CharField(max_length=20)

class Service(models.Model):
    serviceid=models.CharField(max_length=11)
    proid = models.CharField(max_length=11)
    adminID=models.CharField(max_length=11)
    proServicePictureUrl = models.CharField(max_length=500)
    proBeautyCategory = models.CharField(max_length=100)
    proBeautySubCategory = models.CharField(max_length=100)
    proServicePrice = models.CharField(max_length=20)
    proServiceDescription = models.CharField(max_length=4000)
    providerPhotoUrl = models.CharField(max_length=500)
    providerFirstName = models.CharField(max_length=30)
    providerLastName = models.CharField(max_length=30)
    providerEmail = models.CharField(max_length=80)
    providerPhone = models.CharField(max_length=30)
    providerCity = models.CharField(max_length=50)
    providerAddress = models.CharField(max_length=100)
    providerCompany = models.CharField(max_length=50)
    providerToken = models.CharField(max_length=200)
    providerAvailable = models.CharField(max_length=10)
    providerServicePercent = models.CharField(max_length=20)
    providerSalary = models.CharField(max_length=20)
    providerProductSalePercent = models.CharField(max_length=20)
    providerTakeHome = models.CharField(max_length=15)
    managerTakeHome = models.CharField(max_length=15)
    video_url = models.CharField(max_length=500)
    youtube_url = models.CharField(max_length=500)

class ProviderSchedule(models.Model):
    availableid=models.CharField(max_length=11)
    proid=models.CharField(max_length=11)
    availableStart = models.CharField(max_length=80)
    availableEnd = models.CharField(max_length=80)
    availableComment = models.CharField(max_length=2000)

class Product(models.Model):
    itemid=models.CharField(max_length=11)
    proid=models.CharField(max_length=11)
    pictureUrl = models.CharField(max_length=500)
    brand = models.CharField(max_length=80)
    product = models.CharField(max_length=80)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=200)
    price = models.CharField(max_length=20)
    description = models.CharField(max_length=4000)
    inventoryNum = models.CharField(max_length=11)
    saleStatus = models.CharField(max_length=20)
    providerTakeHome = models.CharField(max_length=15)
    managerTakeHome = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    company = models.CharField(max_length=50)
    video_url = models.CharField(max_length=500)
    youtube_url = models.CharField(max_length=500)

class Contactor(models.Model):
    user_email = models.CharField(max_length=80)
    name=models.CharField(max_length=50)
    email = models.CharField(max_length=80)
    photo = models.CharField(max_length=500)
    noti = models.CharField(max_length=5)

class Provider(models.Model):
    proid=models.CharField(max_length=11)
    adminID=models.CharField(max_length=11)
    proProfileImageUrl = models.CharField(max_length=500)
    proFirstName = models.CharField(max_length=50)
    proLastName = models.CharField(max_length=50)
    proEmail = models.CharField(max_length=80)
    proPassword = models.CharField(max_length=30)
    proPhone = models.CharField(max_length=30)
    proCity = models.CharField(max_length=50)
    proAddress = models.CharField(max_length=50)
    proCompany = models.CharField(max_length=50)
    proToken = models.CharField(max_length=500)
    proServicePercent = models.CharField(max_length=8)
    proSalary = models.CharField(max_length=20)
    proProductSalePercent = models.CharField(max_length=20)
    proAvailable = models.CharField(max_length=5)

class AdminUser(models.Model):
    adminID=models.CharField(max_length=11)
    adminEmail=models.CharField(max_length=80)
    adminName = models.CharField(max_length=50)
    adminPassword = models.CharField(max_length=30)
    adminImageUrl = models.CharField(max_length=500)
    adminBroadmoor = models.CharField(max_length=2)
    adminLogoImageUrl = models.CharField(max_length=500)
    adminCompany = models.CharField(max_length=50)

class RetailProduct(models.Model):
    retailid=models.CharField(max_length=11)
    adminID=models.CharField(max_length=11)
    adminEmail = models.CharField(max_length=80)
    adminLogo = models.CharField(max_length=500)
    image = models.CharField(max_length=500)
    name = models.CharField(max_length=300)
    inventorynum = models.CharField(max_length=11)
    category = models.CharField(max_length=100)
    additional = models.CharField(max_length=4000)
    video = models.CharField(max_length=500)
    youtube = models.CharField(max_length=500)

class RetailDetail(models.Model):
    detailid = models.CharField(max_length=11)
    proid=models.CharField(max_length=11)
    size = models.CharField(max_length=100)
    quantity = models.CharField(max_length=11)
    price = models.CharField(max_length=8)

class UserPhoto(models.Model):
    photo_url = models.CharField(max_length=1000)





































