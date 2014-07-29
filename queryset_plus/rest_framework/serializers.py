from queryset_plus.db import queryset_as_dict
from rest_framework import serializers

class QuerySetSerializer(serializers.Serializer):
    #@property
    def data(self):
        """
        Returns the serialized data on the serializer.
        """
        return queryset_as_dict(self.queryset)
        '''
        Runs 'to_native' for each field
        '''

class FullAPISerializer(serializers.Serializer):
    '''
    This is just to have all the functions at hand
    '''

        #####
    # Methods to determine which fields to use when (de)serializing objects.

    def get_default_fields(self):
        """
        Return the complete set of default fields for the object, as a dict.
        """
        return super(self, QuerySetSerializer).get_default_fields()
        '''
        In BaseSerializer, that's empty dict: {}
        In ModelSerializer, that's the model fields.
        '''

    def get_fields(self):
        """
        Returns the complete set of fields for the object as a dict.

        This will be the set of any explicitly declared fields,
        plus the set of fields returned by get_default_fields().
        """
        '''
        what happens if I don't return fields?
        '''
        return super(self, QuerySetSerializer).get_fields()
        '''
        In BaseSerializers, it returns a SortedDict including:


        # Get the explicitly declared fields

        # Add in the default fields

        # If 'fields' is specified, use those fields, in that order.
        if self.opts.fields:
        
        # Remove anything in 'exclude'

        # finally, initialize each of them
        for key, field in ret.items():
            field.initialize(parent=self, field_name=key)

        '''

    #####
    # Methods to convert or revert from objects <--> primitive representations.

    def restore_fields(self, data, files):
        """
        Core of deserialization, together with `restore_object`.
        Converts a dictionary of data into a dictionary of deserialized fields.
        """
        return super(self, QuerySetSerializer).restore_fields(data, files)

    def perform_validation(self, attrs):
        """
        Run `validate_<fieldname>()` and `validate()` methods on the serializer
        """
        return super(self, QuerySetSerializer).perform_validation(attrs)

    def validate(self, attrs):
        """
        Stub method, to be overridden in Serializer subclasses
        """
        return super(self, QuerySetSerializer).validate()

    def restore_object(self, attrs, instance=None):
        """
        Deserialize a dictionary of attributes into an object instance.
        You should override this method to control how deserialized objects
        are instantiated.
        """
        return super(self, QuerySetSerializer).restore_object(attrs, instance)
        '''
        if instance is not None:
            instance.update(attrs)
            return instance
        return attrs
        '''

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        return super(self, QuerySetSerializer).to_native(obj)

    def from_native(self, data, files=None):
        """
        Deserialize primitives -> objects.
        """
        return super(self, QuerySetSerializer).from_native(data, files)
        '''
        Internally uses restore_object
        '''

    def augment_field(self, field, field_name, key, value):
        # This horrible stuff is to manage serializers rendering to HTML
        return super(self, QuerySetSerializer).augment_field(field, field_name, key, value)

    def field_to_native(self, obj, field_name):
        """
        Override default so that the serializer can be used as a nested field
        across relationships.
        """
        return super(self, QuerySetSerializer).field_to_native(obj, field_name)

    def field_from_native(self, data, files, field_name, into):
        """
        Override default so that the serializer can be used as a writable
        nested field across relationships.
        """
        return super(self, QuerySetSerializer).field_from_native(data, files, field_name, into)

    def get_identity(self, data):
        """
        This hook is required for bulk update.
        It is used to determine the canonical identity of a given object.

        Note that the data has not been validated at this point, so we need
        to make sure that we catch any cases of incorrect datatypes being
        passed to this method.
        """
        return super(self, QuerySetSerializer).get_identity(data)
        try:
            return data.get('id', None)
        except AttributeError:
            return None

    #@property
    def errors(self):
        """
        Run deserialization and return error data,
        setting self.object if no errors occurred.
        """
        return super(self, QuerySetSerializer).errors()

    def is_valid(self):
        """
        return not self.errors
        """
        return super(self, QuerySetSerializer).is_valid()
        

    #@property
    def data(self):
        """
        Returns the serialized data on the serializer.
        """        
        return super(self, QuerySetSerializer).data()
        '''
        Runs 'to_native' for each field
        '''
        

    def save_object(self, obj, **kwargs):
        return super(self, QuerySetSerializer).save_object(obj, **kwargs)

    def delete_object(self, obj):
        return super(self, QuerySetSerializer).delete_object(obj)

    def save(self, **kwargs):
        """
        Save the deserialized object and return it.
        """
        return super(self, QuerySetSerializer).save(**kwargs)        

    def metadata(self):
        """
        Return a dictionary of metadata about the fields on the serializer.
        Useful for things like responding to OPTIONS requests, or generating
        API schemas for auto-documentation.
        """
        return super(self, QuerySetSerializer).metadata()
    