from datetime import datetime, timedelta
import graphene
import django_filters
from graphql_jwt.decorators import login_required, permission_required, staff_member_required, superuser_required, user_passes_test
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import Book, BorrowedBook

# get the user model
User = get_user_model()


class BookFilter(django_filters.FilterSet):
    """ 
    Relay allows filtering of data by using filters.
    The fields defined are the filter sets which can be used as arguments when queyring the data.
    """
    
    class Meta:
        model = Book
        fields = "__all__"
        
        
class BookNode(DjangoObjectType):
    """
    The Node class exposes data in a Relay framework.
    The data structure is a bit different from the normal GraphQL data structure.
    The data is exposed through Edges and Nodes.
    Edges: Represents a collection of nodes, which has pagination properties.
    Node: Are the final object or and edge for a new list of objects.
    Graphene will automatically map the model's fields onto the node.
    This is configured in the node's Meta class.
    """
    
    class Meta:
        model = Book
        interfaces = (graphene.relay.Node,)
        
        
class BookFilterConnectionField(DjangoFilterConnectionField):
    """
    Subclass of DjangoFilterConnectionField.
    Defines the connection field, which implements the pagination structure.
    """
    
    class Meta:
        model = Book
        filterset_class = BookFilter
        
        
class BorrowedBookFilter(django_filters.FilterSet):
    """ 
    Relay allows filtering of data by using filters.
    The fields defined are the filter sets which can be used as arguments when queyring the data.
    """
    
    class Meta:
        model = BorrowedBook
        fields = "__all__"
        
        
class BorrowedBookNode(DjangoObjectType):
    """
    The Node class exposes data in a Relay framework.
    The data structure is a bit different from the normal GraphQL data structure.
    The data is exposed through Edges and Nodes.
    Edges: Represents a collection of nodes, which has pagination properties.
    Node: Are the final object or and edge for a new list of objects.
    Graphene will automatically map the model's fields onto the node.
    This is configured in the node's Meta class.
    """
    
    class Meta:
        model = BorrowedBook
        interfaces = (graphene.relay.Node,)
        
        
class BorrowedBookFilterConnectionField(DjangoFilterConnectionField):
    """
    Subclass of DjangoFilterConnectionField.
    Defines the connection field, which implements the pagination structure.
    """
    
    class Meta:
        model = BorrowedBook
        filterset_class = BookFilter

    
        
        
class BorrowBook(graphene.relay.ClientIDMutation):
    """
    Create an entry for book borrowing. In order to create an entry, user must be logged in and must be a librarian to create an entry.
    Pass in the book id, the student id, and optionally a renew flag as the input for book borrowing.
    
    Returns an error if the book has fully been borrowed out or if the student has already reached the maximum number of books allowed to borrow.
    """
    
    borrowed_book: BorrowedBook = graphene.Field(BorrowedBookNode)
    success: bool = graphene.Boolean()
    
    class Input:
        book_id = graphene.ID(required=True)
        student_id = graphene.ID(required=True)
        renew = graphene.Boolean(required=False)
        
    
    @login_required
    @user_passes_test(lambda user: user.role == "librarian")
    def mutate_and_get_payload(root, info, **input):
        book_id = input.get('book_id')
        book = Book.objects.get(id=book_id)
        student_id = input.get('student_id')
        student = User.objects.get(id=student_id)
        renew = input.get('renew')
        
        # check if renew argument is not passed in
        if renew == None:
            renew = False
        
        # get all borrowed books for the student
        borrowed_books = BorrowedBook.objects.filter(student=student, return_date__isnull=True)
        

        # check if student has already borrowed and renewed the book
        if book.id in [borrowed_book.book.id for borrowed_book in borrowed_books if borrowed_book.is_renewed]:
            raise GraphQLError(_("Student has already renewed this book."))
        # check if the book is fully borrowed out
        elif book.available_qty == 0:
            earliest_due_date = book.borrowedbook_set.filter(return_date__isnull=True).order_by('due_date')[0].due_date
            raise GraphQLError(_(f"The book {book.name} is not available. The earliest date it will be available is on {earliest_due_date}."))
        # check if the student has reached the maximum number of books allowed to borrow
        elif borrowed_books.count() == 10:
            raise GraphQLError(_("Student has already borrowed 10 books."))
        # if all checks pass, allow student to borrow the book
        elif book.available_qty > 0 and borrowed_books.count() < 10:
            # check if student can still renew book borrowing
            if renew:
                borrowed_book = book.borrowedbook_set.get(student=student, return_date__isnull=True)
                if datetime.now() > borrowed_book.due_date:
                    raise GraphQLError(_("The book cannot be renewed anymore."))
                
            # create a new borrowed book
            borrow_book = BorrowedBook(
                student=student,
                book=book,
                borrow_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                is_renewed=renew
            )
            borrow_book.save()
            
            # if renew is False, update the book's available qty, else  available_qty remains unchanged
            if not renew:
                book.available_qty -= 1
                book.save()
            
            return BorrowBook(borrowed_book=borrow_book, success=True)
        
        
class ReturnBook(graphene.relay.ClientIDMutation):
    """
    Create an entry for book returns. In order to create an entry, user must be logged in and must be a librarian to create an entry.
    Pass in the book id and the student id as the input for book borrowing.
    
    Returns an error if the book has fully been borrowed out or if the student has already reached the maximum number of books allowed to borrow.
    """
    
    borrowed_book: BorrowedBook = graphene.Field(BorrowedBookNode)
    success: bool = graphene.Boolean()
    
    class Input:
        book_id = graphene.ID(required=True)
        student_id = graphene.ID(required=True)
        
    @login_required
    @user_passes_test(lambda user: user.role == "librarian")
    def mutate_and_get_payload(root, info, **input):
        book_id = input.get('book_id')
        book = Book.objects.get(id=book_id)
        student_id = input.get('student_id')
        student = User.objects.get(id=student_id)
        
        # get all borrowed books for the student
        borrowed_books = BorrowedBook.objects.filter(student=student, return_date__isnull=True)
        
        # check if the book being returned is in the list of books borrowed by the student
        if book.id not in [borrowed_book.book.id for borrowed_book in borrowed_books]:
            raise GraphQLError(_("Student does not have this book borrowed."))
        else:
            # get the borrowed book
            borrowed_book = BorrowedBook.objects.get(student=student, book=book, return_date__isnull=True)
            # set the return date
            borrowed_book.return_date = datetime.now()
            borrowed_book.save()
            # update the book available qty
            book.available_qty += 1
            # save the returned book record
            book.save()
            return ReturnBook(borrowed_book=borrowed_book, success=True)
        

class BookQuery(graphene.ObjectType):
    """
    The BookQuery class defines the query fields for the books.
    """
    
    book = graphene.relay.Node.Field(BookNode)
    books = BookFilterConnectionField(BookNode, filterset_class=BookFilter, description="List of books")
    borrowed_books = BorrowedBookFilterConnectionField(BorrowedBookNode, filterset_class=BorrowedBookFilter, description="List of borrowed books")
    my_books = BorrowedBookFilterConnectionField(BorrowedBookNode, filterset_class=BorrowedBookFilter, description="List of student's borrowed books. Must be logged in as a student to access this field.")
    
    @login_required
    @user_passes_test(lambda user: user.role == "student")
    def resolve_my_books(self, info, **kwargs):
        """
        The my_resolve_books method is used to resolve the books query for a particular logged-in student.
        """
        return BorrowedBook.objects.filter(student=info.context.user)
    

class BookMutation(graphene.ObjectType):
    """
    The BookMutation class defines the mutation fields for the books.
    """
    
    borrow_book = BorrowBook.Field()
    return_book = ReturnBook.Field()