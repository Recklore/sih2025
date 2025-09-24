import React from 'react';
// import { FaFacebook, FaTwitter, FaLinkedin, FaYoutube } from 'react-icons/fa';

// Header component
const Header = () => {
  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-2">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <img src="https://curaj.ac.in/sites/default/files/logo_1.png" alt="CURAJ Logo" className="h-20 mr-4" />
            <div>
              <h1 className="text-xl font-bold text-blue-900">Central University of Rajasthan</h1>
              <p className="text-sm text-gray-600">A Central University established by an Act of Parliament</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">Thursday, September 25, 2025</p>
              <div className="flex space-x-2 mt-1">
                 <button className="bg-gray-200 px-2 py-1 rounded">A-</button>
                 <button className="bg-gray-200 px-2 py-1 rounded">A</button>
                 <button className="bg-gray-200 px-2 py-1 rounded">A+</button>
              </div>
            </div>
            <button className="bg-orange-500 text-white px-4 py-2 rounded">Login</button>
          </div>
        </div>
      </div>
    </header>
  );
};


// Navigation Bar component
const NavigationBar = () => {
  const navItems = ['Home', 'About', 'Vision and Mission', 'ODL/QP', 'Academics', 'Accreditation and Rankings', 'Students Facilities', 'IQAC', 'Governance'];
  return (
    <nav className="bg-blue-800 text-white">
      <div className="container mx-auto px-4">
        <ul className="flex justify-center space-x-6 py-3">
          {navItems.map(item => <li key={item}><a href="#" className="hover:text-yellow-300">{item}</a></li>)}
        </ul>
      </div>
    </nav>
  );
};


// News, Achievements, and Admission Section
const MainContent = () => {
    return (
        <section className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="bg-gray-100 p-6 rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-blue-900 mb-4 border-b-2 border-blue-900 pb-2">News & Events</h2>
                    <p className="text-gray-700 mb-4">GST on accommodation service at guest house has been reduced from 12% to 3% which is applicable only when employee & students are exempted from GST claim.</p>
                    <p className="text-sm text-gray-500 mb-4">23-Sep-2025</p>
                    <button className="bg-blue-600 text-white px-6 py-2 rounded-full hover:bg-blue-700">Read More</button>
                </div>
                <div className="bg-gray-100 p-6 rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-green-700 mb-4 border-b-2 border-green-700 pb-2">Achievements</h2>
                    <p className="text-gray-700 mb-4">Central University of Rajasthan Rank as 'MENTOR' University in National Ranking framework university.</p>
                     <p className="text-sm text-gray-500 mb-4">22-Sep-2025</p>
                    <button className="bg-green-600 text-white px-6 py-2 rounded-full hover:bg-green-700">Read More</button>
                </div>
                <div className="bg-gray-100 p-6 rounded-lg shadow-md">
                    <h2 className="text-2xl font-bold text-purple-700 mb-4 border-b-2 border-purple-700 pb-2">Admission</h2>
                    <p className="text-gray-700 mb-4">Provisional Admission offered in UG & PG Programmes after University Level Entrance Exam on 11-12.09.2025.</p>
                     <p className="text-sm text-gray-500 mb-4">22-Sep-2025</p>
                    <button className="bg-purple-600 text-white px-6 py-2 rounded-full hover:bg-purple-700">Read More</button>
                </div>
            </div>
        </section>
    );
}

// QuickLinks and Opportunities
const QuickLinksAndOpportunities = () => {
    const quickLinks = [
        "Achievements", "Central Library", "Convocation", "Exams & Results", "Recruitments",
        "Admission", "Conference & Workshop", "IPR & Research Position", "Incubation Cell", "Tenders"
    ];
    return (
        <section className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
                <div className="md:col-span-2 grid grid-cols-2 gap-4">
                    {quickLinks.map(link => (
                        <a key={link} href="#" className="bg-white p-3 rounded-md shadow flex items-center hover:bg-gray-100 transition">
                             <span className="bg-blue-500 w-2 h-6 mr-3"></span>
                            {link}
                        </a>
                    ))}
                </div>
                <div className="space-y-6">
                    <div className="bg-blue-200 p-6 rounded-lg shadow-md text-center">
                        <h3 className="text-2xl font-bold text-blue-900">Job Opportunities</h3>
                        <button className="mt-4 bg-blue-700 text-white px-6 py-2 rounded-full text-lg">›</button>
                    </div>
                    <div className="bg-green-200 p-6 rounded-lg shadow-md text-center">
                        <h3 className="text-2xl font-bold text-green-900">Training and Placements</h3>
                        <button className="mt-4 bg-green-700 text-white px-6 py-2 rounded-full text-lg">›</button>
                    </div>
                </div>
            </div>
             <div className="flex justify-center items-center mt-12">
                <div className="text-center p-6 border-2 border-yellow-400 rounded-lg bg-white shadow-lg">
                    <p className="text-4xl font-extrabold text-yellow-500">A++</p>
                    <p className="text-gray-700 font-semibold">Accredited with A++ Grade By</p>
                    <p className="text-xl font-bold text-blue-900">NAAC</p>
                    <p className="mt-2 text-sm text-gray-600">NIRF Rank 2025</p>
                    <p className="font-bold text-lg">89</p>
                </div>
            </div>
        </section>
    );
};


// Footer component
const Footer = () => {
    return (
        <footer className="bg-gray-800 text-white mt-12">
            <div className="container mx-auto px-4 py-8">
                <div className="flex justify-between items-center">
                    <div>
                        <h4 className="font-bold mb-2">Important Links</h4>
                        <img src="https://curaj.ac.in/sites/default/files/moe-logo.png" alt="Ministry of Education" className="h-10 inline-block mr-4" />
                        <img src="https://curaj.ac.in/sites/default/files/swayam-logo.png" alt="Swayam" className="h-10 inline-block mr-4" />
                        <img src="https://curaj.ac.in/sites/default/files/abc.png" alt="ABC" className="h-10 inline-block" />
                    </div>
                    <div>
                        <h4 className="font-bold mb-2">Social Links</h4>
                        <div className="flex space-x-4">
                            {/* <a href="#" className="text-2xl hover:text-blue-400"><FaFacebook /></a>
                            <a href="#" className="text-2xl hover:text-blue-400"><FaTwitter /></a>
                            <a href="#" className="text-2xl hover:text-blue-400"><FaLinkedin /></a>
                            <a href="#" className="text-2xl hover:text-red-500"><FaYoutube /></a> */}
                        </div>
                    </div>
                </div>
                <div className="text-center text-gray-400 mt-8 pt-4 border-t border-gray-700">
                    <p>&copy; 2025 Central University of Rajasthan. All Rights Reserved.</p>
                </div>
            </div>
        </footer>
    );
};

// Main App component
export default function Home() {
  return (
    <div className="bg-gray-50">
      <Header />
      <NavigationBar />
      <div className="relative h-64 bg-cover bg-center" style={{ backgroundImage: "url('https://curaj.ac.in/sites/default/files/DSC_0156.JPG')" }}>
        <div className="absolute inset-0 bg-black opacity-30"></div>
         <div className="relative container mx-auto px-4 h-full flex items-center justify-center">
              <h2 className="text-white text-4xl font-bold text-center">Rajasthan Kendriya Vishwavidyalaya<br/>NAAC 'A++' Grade</h2>
        </div>
      </div>
      <MainContent />
      <QuickLinksAndOpportunities />
      <Footer />
    </div>
  );
}