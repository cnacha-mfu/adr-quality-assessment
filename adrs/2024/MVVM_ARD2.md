# Title
Theme or Template of the application

## Context
What is the issue that we're seeing that is motivating this decision or change?
-Every application that we try to develop needs to have a good design, and nowadays, many applications incorporate what we refer to as a theme. It would be fantastic to have a very easy way to manage the theme's appearance for our application.

## Decision
What is the solution that we're proposing and/or doing?
-We choose MVVM to focus on our design of template or theme.

## Rationale
Why do we choose this solution?
-In the MVVM architecture, separating the view from the logic makes it possible to have different teams work on different components simultaneously. The View is responsible for defining the structure, layout, and appearance of what users see on the screen. Ideally, this allows us to focus on our template and theme for our application

## Consequences
Pros – What becomes easier?
-To focus only on the View part first, then we can easily combine it later with the ViewModel part and the model.
-It's easy to fix, delete, and add to the View however we want.
-We can remain agile and keep releasing successive versions quickly.

Cons – What becomes more difficult?
-Because the View is related to the ViewModel, every edit in the view part will always affect the ViewModel part, and we need to check and edit the ViewModel part every time too.
-Debugging is a bit difficult.


## Sample code
Give some sample code related to this decision.

*Java

// MARK: - View
public class PetView: UIView {
  public let imageView: UIImageView
  public let nameLabel: UILabel
  public let ageLabel: UILabel
  public let adoptionFeeLabel: UILabel
  
  public override init(frame: CGRect) {
    
    var childFrame = CGRect(x: 0, y: 16,
                            width: frame.width,
                            height: frame.height / 2)
    imageView = UIImageView(frame: childFrame)
    imageView.contentMode = .scaleAspectFit
    
    childFrame.origin.y += childFrame.height + 16
    childFrame.size.height = 30
    nameLabel = UILabel(frame: childFrame)
    nameLabel.textAlignment = .center
    
    childFrame.origin.y += childFrame.height
    ageLabel = UILabel(frame: childFrame)
    ageLabel.textAlignment = .center
    
    childFrame.origin.y += childFrame.height
    adoptionFeeLabel = UILabel(frame: childFrame)
    adoptionFeeLabel.textAlignment = .center
    
    super.init(frame: frame)
    
    backgroundColor = .white
    addSubview(imageView)
    addSubview(nameLabel)
    addSubview(ageLabel)
    addSubview(adoptionFeeLabel)
  }
  
  @available(*, unavailable)
  public required init?(coder: NSCoder) {
    fatalError("init?(coder:) is not supported")
  }
}

  *This code is an example of the template for a pet view for our pet care application on our project. 
   -This code creates a PetView with four subviews: an imageView to display the pet’s image and three other labels to display the pet’s name, age, and adoption fee. Inside this initializer, it sets up the frame for each subview (imageView, nameLabel, ageLabel, adoptionFeeLabel) based on the given frame parameter. 
   -It configures each label with appropriate text alignment, sets up the background color, and adds all the subviews.