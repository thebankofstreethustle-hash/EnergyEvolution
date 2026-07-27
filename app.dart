import 'package:flutter/material.dart';
import 'api.py' as api;

void main() => runApp(EnergyEvolutionApp());

class EnergyEvolutionApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EnergyEvolution OS',
      home: Scaffold(
        appBar: AppBar(title: Text('EnergyEvolution OS')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Waste Heat Recovery Optimizer', style: TextStyle(fontSize: 20)),
              SizedBox(height: 20),
              Text('Engine: waste_heat_optimizer.py'),
              Text('Backend: api.py'),
              Text('Status: LIVE'),
            ],
          ),
        ),
      ),
    );
  }
}
