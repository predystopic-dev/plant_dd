"use client";
import { ThemeToggle } from "@/components/ui/theme-toggle"
import { siteConfig } from "@/config/site"
import Link from "next/link"
import { useEffect, useState } from "react";
import { SelectPicker } from "rsuite";
import { getCookie, hasCookie, setCookie } from 'cookies-next';



export function Navbar() {
  const languages = [
    { label: 'English', value: '/auto/en' },
    { label: `Marathi`, value: '/auto/mar' },
    { label: 'Hindi', value: '/auto/hi' },
    { label: 'Bhojpuri', value: '/auto/bho' },
    ];

  const [selected, setSelected] = useState('')
  useEffect(() => {
    var addScript = document.createElement('script');
    addScript.setAttribute('src', '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit');
    document.body.appendChild(addScript);
    window.googleTranslateElementInit = googleTranslateElementInit;
  }, [])

  //if (hasCookie('googtrans')) {
  //  setSelected(getCookie('googtrans'))
  //}
  //else {
  //  setSelected('/auto/en')
  //}

  const googleTranslateElementInit = () => {

    new window.google.translate.TranslateElement({
      pageLanguage: 'auto',
      autoDisplay: false,
      includedLanguages: "mr,en,hi,bho", // If you remove it, by default all google supported language will be included
      layout: google.translate.TranslateElement.InlineLayout.SIMPLE
    },
      'google_translate_element');
  }

  //const langChange = (e: any, m: any, evt: any) => {
  //  evt.preventDefault()
  //  if (hasCookie('googtrans')) {
  //    setCookie('googtrans', decodeURI(e))
  //    setSelected(e)
  //  }
  //  else {
  //    setCookie('googtrans', e)
  //    setSelected(e)
  //  }
  //  window.location.reload()
  //}


  return (

    <nav className="flex fixed w-full backdrop-blur-sm items-center px-4 py-4 justify-between z-50">
      <div className="flex gap-8 items-center">
        <div>
          <p className="scroll-m-20 text-xl font-semibold">
            <Link href="/">{siteConfig.name}</Link>
          </p>
        </div>
        <ul className="flex gap-4">
          {/* TODO: Add Effects */}
          <li className="cursor-pointer hover:underline">
            <Link href="/home">Home</Link>
          </li>
          <li className="cursor-pointer hover:underline">
            <Link href="/about">About</Link>
          </li>
          <li>
            <div id="google_translate_element"></div>
            <SelectPicker
              data={languages}
              style={{ width: 100 }}
              placement="bottomEnd"
              cleanable={false}
              value={selected}
              searchable={false}
              className={'notranslate'}
              menuClassName={'notranslate'}
              //onSelect={(e, m, evt) => langChange(e, m, evt)}
              placeholder="Lang" />
          </li>
        </ul>
      </div>
      <ThemeToggle />
    </nav>
  )
}
