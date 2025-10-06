import '/flutter_flow/flutter_flow_util.dart';
import '/index.dart';
import 'personalization_widget.dart' show PersonalizationWidget;
import 'package:flutter/material.dart';

class PersonalizationModel extends FlutterFlowModel<PersonalizationWidget> {
  ///  Local state fields for this page.

  double chillAllInValue = 5.0;

  double quickHitsDeepDivesValue = 5.0;

  double templeFoodiePopCultureValue = 5.0;

  ///  State fields for stateful widgets in this page.

  // State field(s) for TextField widget.
  FocusNode? textFieldFocusNode;
  TextEditingController? textFieldTextController;
  String? Function(BuildContext, String?)? textFieldTextControllerValidator;
  // State field(s) for Slider widget.
  double? sliderValue1;
  // State field(s) for Slider widget.
  double? sliderValue2;
  // State field(s) for Slider widget.
  double? sliderValue3;

  @override
  void initState(BuildContext context) {}

  @override
  void dispose() {
    textFieldFocusNode?.dispose();
    textFieldTextController?.dispose();
  }
}
