Title 
Adding search and filter function with Laravel

Context
Our dormitory renting application does not have a filtering function. This is not convenient for users to find dormitories which are in their preferred range. Adding that function would be helpful for users to find the suitable dormitory accommodation and improve their satisfaction. 

Decision
Determine the search and filter feature that is available for finding the desired dormitories by users based on the users’ need such as location, price, room type and dates.

Rationale
Enhancing the search and filtering feature will empower users to search for desired information. Once the users search for dormitories in a specific location, the feature will filter and show the users with the specific dormitories that the users want and meet with their desires which can improve in user satisfaction.

Consequences

Pros
Client-side filtering provides users a more dynamic and flexible filtering experience, enabling them to quickly find relevant dorm listings based on their preferences and perfect results as needed.
Cons
Additional development work is needed to handle local information storage, design and implement the filtering method, and ensure platform and device compatibility for implementing client-side filtering. Complexity may lead to longer development cycles, increased testing requirements, and higher maintenance overhead.

Sample Codes


Routes
use App\Http\Controllers\DormitoryController;

Route::get('/dormitories', [DormitoryController::class, 'index'])->name('dormitories.index');

Controller
namespace App\Http\Controllers;

use App\Models\Dormitory;
use Illuminate\Http\Request;

class DormitoryController extends Controller
{
    public function index(Request $request)
    {
        $query = Dormitory::query();

        // Filter by location
        if ($request->has('location')) {
            $query->where('location', $request->input('location'));
        }

        // Filter by capacity
        if ($request->has('capacity')) {
            $query->where('capacity', '>=', $request->input('capacity'));
        }

        // Search by name
        if ($request->has('search')) {
            $query->where('name', 'like', '%' . $request->input('search') . '%');
        }

        // Get the filtered and paginated results
        $dormitories = $query->paginate(10);

        return view('dormitories.index', compact('dormitories'));
    }
}

View
<form action="{{ route('dormitories.index') }}" method="GET">
    <input type="text" name="search" placeholder="Search by name">
 <select name="location">
        <option value="">-- Select location --</option>
        <option value="location1">Location 1</option>
        <option value="location2">Location 2</option>
        <!-- Add more options as needed -->
    </select>
    <input type="number" name="capacity" placeholder="Minimum capacity">
    <button type="submit">Search</button>
</form>

@foreach ($dormitories as $dormitory)
    <!-- Display dormitory details here -->
    <p>{{ $dormitory->name }}, Location: {{ $dormitory->location }}, Capacity: {{ $dormitory->capacity }}</p>
@endforeach

{{ $dormitories->links() }}
