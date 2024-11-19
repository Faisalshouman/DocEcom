from rest_framework.permissions import IsAdminUser
                                        
                                        class ProductListCreateView(APIView):
                                            throttle_classes = [UserRateThrottle]
                                            permission_classes = [IsAdminUser]
                                        
                                            def get(self, request):
                                                # Apply pagination and throttling
                                                products = Product.objects.all()
                                                paginator = PageNumberPagination()
                                                result_page = paginator.paginate_queryset(products, request)
                                                serializer = ProductSerializer(result_page, many=True)
                                                return paginator.get_paginated_response(serializer.data)
                                        
                                            def post(self, request):
                                                serializer = ProductSerializer(data=request.data)
                                                if serializer.is_valid():
                                                    serializer.save()
                                                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                                                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)