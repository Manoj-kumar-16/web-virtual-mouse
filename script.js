
function validateLogin() {
  const user = document.getElementById('username').value.trim();
  const mobile = document.getElementById('mobile').value.trim();
  const email = document.getElementById('email').value.trim();
  if (user && /^\d{10}$/.test(mobile) && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    localStorage.setItem('username', user);
    localStorage.setItem('mobile', mobile);
    localStorage.setItem('email', email);
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('homePage').style.display = 'block';
    document.getElementById('name').value = user;
    document.getElementById('emailInfo').value = email;
    document.getElementById('mobileInfo').value = mobile;
  } else {
    alert('Enter valid login details');
  }
}
