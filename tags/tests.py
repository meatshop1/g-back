from django.test import TestCase

# Create your tests here.
# tags/tests.py

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from shop.models import Product, Collection
from tags.models import Tag, TaggedItem
from decimal import Decimal


class TagModelTests(TestCase):
    def test_tag_creation(self):
        """Test creating a tag is successful"""
        tag = Tag.objects.create(label='Fresh')
        self.assertEqual(str(tag), 'Fresh')
        self.assertEqual(tag.label, 'Fresh')


class TaggedItemModelTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(label='Premium')
        self.collection = Collection.objects.create(title='Test Collection')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection
        )
        
    def test_tagged_item_creation(self):
        """Test tagging an item is successful"""
        content_type = ContentType.objects.get_for_model(Product)
        
        tagged_item = TaggedItem.objects.create(
            tag=self.tag,
            content_type=content_type,
            object_id=self.product.id
        )
        
        self.assertEqual(tagged_item.tag, self.tag)
        self.assertEqual(tagged_item.content_type, content_type)
        self.assertEqual(tagged_item.object_id, self.product.id)
        
        # Test the generic foreign key
        self.assertEqual(tagged_item.content_object, self.product)
    
    def test_find_tagged_items(self):
        """Test finding all items with a specific tag"""
        content_type = ContentType.objects.get_for_model(Product)
        
        # Create multiple tagged items
        tagged_item1 = TaggedItem.objects.create(
            tag=self.tag,
            content_type=content_type,
            object_id=self.product.id
        )
        
        # Create another product and tag it
        product2 = Product.objects.create(
            name='Another Product',
            description='Another description',
            price=Decimal('49.99'),
            inventory=5,
            collection=self.collection
        )
        
        tagged_item2 = TaggedItem.objects.create(
            tag=self.tag,
            content_type=content_type,
            object_id=product2.id
        )
        
        # Query all tagged items with our tag
        tagged_items = TaggedItem.objects.filter(tag=self.tag)
        
        self.assertEqual(tagged_items.count(), 2)
        self.assertIn(tagged_item1, tagged_items)
        self.assertIn(tagged_item2, tagged_items)
