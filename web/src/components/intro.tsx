import { Button } from "@/components/ui/button"
import Image from "next/image"
import Link from "next/link"
import amma from "@/assets/indian_crop_6.jpg"
import GreenLeaves from "@/assets/green-leaves.jpg"
import clickimg from "@/assets/click-photo.jpg"
import Logo from "@/assets/logo.png"
import ScrollDown from "@/components/scroll-down"
import { siteConfig } from "@/config/site"

export default function Introduction() {
  return (
    <section className="py-4 md:py-0 min-h-screen grid md:grid-cols-1 place-items-center">
      
      <div className="relative hidden md:block md:w-full md:h-full">
        <Image
          src={amma}
          alt="Green and Healthy Leaves"
          fill
          priority
          quality={100}
          className="hidden md:block"
        />
      </div>
      <div className="absolute w-11/12 md:w-1/2 flex flex-col items-center text-center rgba(255,255,255,0.18)">
        {/* TODO: Replace Logo Later */}
        <Image
          src={Logo}
          alt={`${siteConfig.name} Logo`}
          width={150}
          className="md:hidden"
        />
        <h1 className="scroll-m-20 mb-4 text-4xl font-extrabold tracking-tight lg:text-5xl uppercase gradient-text">
          {siteConfig.name}
        </h1>
        <p className="text-center text-sm md:text-base mt-6">
          {siteConfig.description}
        </p>
        <Button className="my-7" asChild>
          <Link href="/home">Use {siteConfig.name}</Link>
        </Button>
      </div>
      
      <ScrollDown />
    </section>
  )
}
