from django.http import HttpResponse
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Role, Quota
from .serializers import UserSerializer, UserRegistrationSerializer, RoleSerializer, QuotaSerializer

def index(request):
    return HttpResponse("Users index")

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限，只允许管理员创建和修改，其他用户只读。
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集，提供用户管理的CRUD操作。
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # 只有管理员可以管理用户

    @action(detail=True, methods=['get', 'put'], serializer_class=QuotaSerializer)
    def quota(self, request, pk=None):
        """
        获取或更新用户配额
        """
        user = self.get_object()
        quota, created = Quota.objects.get_or_create(user=user)
        if request.method == 'PUT':
            serializer = QuotaSerializer(quota, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = QuotaSerializer(quota)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], serializer_class=RoleSerializer)
    def roles(self, request, pk=None):
        """
        获取或分配用户角色
        """
        user = self.get_object()
        if request.method == 'POST':
            role_id = request.data.get('role_id')
            try:
                role = Role.objects.get(id=role_id)
                user.role = role
                user.save()
                return Response(UserSerializer(user).data)
            except Role.DoesNotExist:
                return Response({'error': '角色不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.role:
            return Response(RoleSerializer(user.role).data)
        return Response({})


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色视图集
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]


class UserRegistrationView(generics.CreateAPIView):
    """
    用户注册视图
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # 允许任何人注册

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户个人资料视图
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class CustomTokenObtainPairView(TokenObtainPairView):
    # 你可以在这里自定义token响应
    pass
