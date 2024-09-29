import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ProductListScreen extends StatefulWidget {
  final int? vendorId;

  ProductListScreen({this.vendorId});

  @override
  _ProductListScreenState createState() => _ProductListScreenState();
}

class _ProductListScreenState extends State<ProductListScreen> {
  List products = [];
  bool isLoading = true;
  String message = '';

  @override
  void initState() {
    super.initState();
    fetchProducts();
  }

  void fetchProducts() async {
    String url = 'http://10.0.2.2:8000/products';
    if (widget.vendorId != null) {
      url += '?vendor_id=${widget.vendorId}';
    }
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      setState(() {
        products = json.decode(response.body)['products'];
        isLoading = false;
      });
    } else if (response.statusCode == 202) {
      // Veri çekiliyor, biraz bekleyip tekrar dene
      setState(() {
        message = 'Data is being fetched, please wait...';
      });
      Future.delayed(Duration(seconds: 5), fetchProducts);
    } else {
      setState(() {
        message = 'Failed to load products';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: Text('Product List'),
        ),
        body: Center(
          child: message.isEmpty ? CircularProgressIndicator() : Text(message),
        ),
      );
    } else {
      return Scaffold(
        appBar: AppBar(
          title: Text('Product List'),
        ),
        body: ListView.builder(
          itemCount: products.length,
          itemBuilder: (context, index) {
            final product = products[index];
            return ListTile(
              leading:
                  Image.asset('assets/images/image.png'), // Varsayılan resim
              title: Text(product['name']),
              subtitle: Text('\$${product['price']}'),
            );
          },
        ),
      );
    }
  }
}
