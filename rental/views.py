from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserSerializer, CarSerializer, RentSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .models import Car, Rent
from rest_framework.authtoken.models import Token
from django.db import transaction

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            return Response({'status': 'Account created', 'user_id': serializer.data.id, 'status_code': 200}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'access_token': token.key, 'status': 'Login successful', 'user_id': user.id, 'status_code': 200})
        return Response({'status': 'Incorrect usernae / password, retry', 'status_code': 401}, status=status.HTTP_401_UNAUTHORIZED)

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminUser]
        elif self.action == 'available_rentals':
            permission_classes = [AllowAny]
        elif self.action == 'rent':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def create(self, request):
        print("test")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': 'Car added successfully',
            'car_id': serializer.data['id'],
            'status_code': status.HTTP_201_CREATED
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def available_rentals(self, request):
        origin = request.query_params.get('origin')
        category = request.query_params.get('category')
        hours = int(request.query_params.get('required_hours'))
        available_rents = Car.objects.filter(current_city=origin)
        
        rentals = []
        for rent in available_rents:
            total_amount = rent.rent_per_hr * hours
            rental_data = {
                'id': rent.id,
                'model': rent.model,
                'rent_per_hr': rent.rent_per_hr,
                'total_amount': total_amount,
                'current_city': rent.current_city,
                'rent_history': rent.rent_history
            }
            rentals.append(rental_data)
        
        serializer = self.get_serializer(rentals, many=True)
        return Response(rentals)
    
    @action(detail=False, methods=['post'])
    def rent(self, request):
        car_id = request.data.get('car_id')
        origin = request.data.get('origin')
        destination = request.data.get('destination')
        hours = int(request.data.get('hours_requirement'))
        car = Car.objects.get(id=car_id)
        with transaction.atomic():
            rent = Rent.objects.create(car=car, origin=origin, destination=destination, hours_requirement=hours, total_payable_amt=car.rent_per_hr * hours)
            car.rent_history.append(rent.id)
            car.save()
        return Response({'status': 'Rent created', 'rent_id': rent.id, 'status_code': 200}, status=status.HTTP_201_CREATED)