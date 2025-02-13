# TODO

- Add step in float range too - but float ranges do not exist in core Python, so the functionality would have to be created manually. also, currently the only use of float ranges in Obs Test Tool is to create a random float value between start an end, which does not have step as an option.
- Add step in duration - between time A and B at every X units, but this is effectively already available with startOffset, endOffest and frequency, so it could only be of use as a shortcut when random frequency is not required.
- Conform to the requirements of Schema Store
  
  https://github.com/SchemaStore/schemastore/blob/master/CONTRIBUTING.md

# IN PROGRESS

_Nothing here at the moment._

# DONE

- Add schema information for `config.yaml`
  
  https://medium.com/@alexmolev/boost-your-yaml-with-autocompletion-and-validation-b74735268ad7

  https://json-schema.org/learn/getting-started-step-by-step

  https://json-schema.org/learn/json-schema-examples#device-type: this should help with the definition of "timings" repeated in both logging and monitoring jobs
