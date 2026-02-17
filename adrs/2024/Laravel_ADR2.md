#Context:
The situation where users of a dorm-finding app are unable to meet with landlords directly

#Decision:
To address the restrictions of users being unable to meet landlords personally, employ a combination of virtual tours, video conversations, thorough information, reviews and ratings, transparent communication, online booking and payment, and trust-building methods.

#Rationale:
Virtual tours and detailed information:Virtual tours and detailed information give customers a thorough overview of the dormitories, allowing them to make informed decisions without having to physically visit.
Video Calls: Video calls enable direct communication between users and landlords, fostering trust and addressing specific queries or concerns in real-time.
Reviews and Ratings: Reviews and ratings offer valuable insights from previous tenants, helping prospective users assess the quality and suitability of the dormitories.
Transparent Communication: Transparent communication about the intermediary role of the application builds trust and clarity among users and landlords regarding the rental process.
Online Booking and Payment: Online booking and payment streamline the rental process, offering convenience and security for both parties involved.
Trust Building: By providing excellent customer service and ensuring a smooth user experience, trust in the application as a reliable platform for dormitory finding is established.

#Consequences:
#Pros:
-Improved user experience: Users can save time and effort by communicating with landlords and online exploring dorms.
-Enhanced honesty: The application gains trust and reliability from detailed data, honest reviews, and open communication.
-Simplified process: Renting is made easier for both tenants and landlords with online booking and payment.
-Better ability to make decisions Reviews, video calls, and virtual tours all assist users in making well-informed -decisions when renting dorm rooms.

#Cons:
-Dependency on technology: Those with limited access to technology or internet connectivity may find it difficult to depend only on virtual communication methods.
-Trust issues: Despite initiatives to build trust, some users might still favor in-person contacts with landlords, which could cause hesitation or doubt.
-Possibility of error: Detailed information and virtual tours might not always correctly show the real state of the dorms, which could cause conflicts or misunderstandings.
-Increased workload: The application team needs to put in more time and resources to manage online bookings, video calls, reviews, and virtual tours.


#Sample Code

#Define Dormitory Model

// app/Models/Dormitory.php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Dormitory extends Model
{
    protected $fillable = ['name', 'location', 'price'];
}


#Create Dormitory Controller

// app/Http/Controllers/DormitoryController.php

namespace App\Http\Controllers;

use App\Models\Dormitory;
use Illuminate\Http\Request;

class DormitoryController extends Controller
{
    public function index()
    {
        $dormitories = Dormitory::all();
        return response()->json($dormitories);
    }
}


#Define Route

// routes/api.php

use App\Http\Controllers\DormitoryController;

Route::get('/dormitories', [DormitoryController::class, 'index']);


// routes/api.php

use App\Http\Controllers\DormitoryController;

Route::get('/dormitories', [DormitoryController::class, 'index']);


#Seed Dormitory Table

// database/seeders/DormitorySeeder.php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Dormitory;

class DormitorySeeder extends Seeder
{
    public function run()
    {
        Dormitory::create([
            'name' => 'Cozy Dormitory',
            'location' => 'City Center',
            'price' => 500
        ]);

        Dormitory::create([
            'name' => 'Modern Dormitory',
            'location' => 'Suburbia',
            'price' => 600
        ]);
    }
}


#Run Seeder

php artisan db:seed --class=DormitorySeeder








