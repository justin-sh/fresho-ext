import csv
import logging
from io import TextIOWrapper

from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.utils.datastructures import MultiValueDict
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import UserSerializer

logger = logging.getLogger()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def upload_orders(requests: Request):
    logger.info("---------")
    logger.info("---------")
    logger.info("---------")
    logger.info("---------")
    files: MultiValueDict = requests.FILES
    if files and len(files) != 1:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    logger.info("---------" + ",".join(files.dict()))
    order_file: UploadedFile = files.get("yes")
    logger.info(order_file.name)
    logger.info(order_file.size)
    logger.info(order_file.charset)
    # logger.info(order_file.readlines())

    if order_file.size > 1 * 1024 * 1024:
        return Response("File is too big", status=status.HTTP_400_BAD_REQUEST)

    f = TextIOWrapper(order_file, encoding="utf-8", newline="")
    reader = csv.DictReader(f)
    # # logger.info(reader.line_num)
    logger.info(reader.fieldnames)
    for x in reader:
        logger.info(x)
    # logger.info(reader.fieldnames)
    # reader.__init__()

    return Response("ok")
