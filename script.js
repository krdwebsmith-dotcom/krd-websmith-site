
const header=document.getElementById("siteHeader");
const menuToggle=document.getElementById("menuToggle");
const mobileMenu=document.getElementById("mobileMenu");

window.addEventListener("scroll",()=>{
  header.classList.toggle("scrolled",window.scrollY>30);
},{passive:true});

menuToggle.addEventListener("click",()=>{
  const open=mobileMenu.classList.toggle("open");
  menuToggle.classList.toggle("active",open);
  menuToggle.setAttribute("aria-expanded",String(open));
  document.body.classList.toggle("menu-open",open);
});

mobileMenu.querySelectorAll("a").forEach(link=>link.addEventListener("click",()=>{
  mobileMenu.classList.remove("open");
  menuToggle.classList.remove("active");
  document.body.classList.remove("menu-open");
}));

const observer=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    }
  });
},{threshold:.12});

document.querySelectorAll(".reveal").forEach(el=>observer.observe(el));
document.getElementById("year").textContent=new Date().getFullYear();
