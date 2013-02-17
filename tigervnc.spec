# snapshotver is year-month-day-svnrevision, generated by "make dist"
%define snapshot        0
%define snapshotversion 201211265015
%define rel             1

Name:		tigervnc
Version:	1.2.80
%if %{snapshot}
Release:	0.%{snapshotversion}.%{rel}
%else
Release:	%{rel}
%endif

License:	GPLv2+
URL:		http://www.tigervnc.com/
Source0:	%{name}-%{version}.tar.gz
Source1:	vncviewer.desktop
# Missing from "make dist":
Source2:	%{name}-media.tar.gz
# fedora patches
Patch4:		tigervnc-cookie.patch
Patch10:	tigervnc12-ldnow.patch
Patch11:	tigervnc12-gethomedir.patch
Patch13:	tigervnc11-rh692048.patch
Patch14:	tigervnc12-xorg113-glx.patch

#(proyvind): FIXME: this one got fscked, needs to be fixed in Makefile.am, so
# that miext/sync/libsync.la gets built first...
#Patch18: tigervnc-1.0.90-link-against-forgotten-local-library.patch

BuildRequires:	x11-server-source
BuildRequires:	gettext-devel
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xi)
BuildRequires:	pkgconfig(xtst)
BuildRequires:	x11-font-util
BuildRequires:	x11-util-macros
BuildRequires:	pkgconfig(xtrans)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(xkbfile)
BuildRequires:	pkgconfig(xfont)
BuildRequires:	pkgconfig(pixman-1)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(pciaccess)
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(gnutls)
BuildRequires:	imagemagick
BuildRequires:	nasm
#BuildRequires:	java-devel
BuildRequires:	autoconf
BuildRequires:	java-1.6.0-openjdk-devel
BuildRequires:	cmake
BuildRequires:	fltk-devel

#------------------------------------------------------------------------------

# package tigervnc

Summary:	Viewer for the VNC remote display system
Group:		Networking/Remote access

# Old RealVNC package:
Provides:	vncviewer
Conflicts:	tightvnc

%description
Virtual Network Computing (VNC) is a remote display system which
allows you to view a computing 'desktop' environment not only on the
machine where it is running, but from anywhere on the Internet and
from a wide variety of machine architectures.  This package contains a
client which will allow you to connect to other desktops running a VNC
server.

%files -f %{name}.lang
%doc README.txt
%{_bindir}/vncviewer
%{_iconsdir}/*
%{_datadir}/applications/*
%{_mandir}/man1/vncviewer.1*


#------------------------------------------------------------------------------

%package server

Summary:	Server for the VNC remote display system
Group:		Networking/Remote access

# Old RealVNC package:
Provides:	vnc-server
Conflicts:	tightvnc-server

Requires:	vnc-server-common

%description server
The VNC system allows you to access the same desktop from a wide
variety of platforms.  This package is a TigerVNC server, allowing
others to access the desktop on your machine.

%files server
%{_bindir}/vncconfig
%{_bindir}/vncpasswd
%{_bindir}/x0vncserver
%{_bindir}/Xvnc
%{_bindir}/vncserver
%{_mandir}/man1/Xvnc.1*
%{_mandir}/man1/vncpasswd.1*
%{_mandir}/man1/vncconfig.1*
%{_mandir}/man1/vncserver.1*
%{_mandir}/man1/x0vncserver.1*

#------------------------------------------------------------------------------

%package server-module

Summary:	Xorg module for the VNC remote display system
Group:		Networking/Remote access

Provides:	vnc-server-module

Requires:	x11-server-xorg

%description server-module
This package contains libvnc.so module to X server, allowing others
to access the desktop on your machine.

%files server-module
%{_libdir}/xorg/modules/extensions/libvnc.so

#------------------------------------------------------------------------------

%package java

Summary:	Java viewer for the VNC remote display system
Group:		Networking/Remote access

# Old RealVNC package:
Provides:	vnc-java
Conflicts:	tightvnc-java

# "TightVNC-specific" is not a typo, see the README file located inside the
# java source tree
%description java
This distribution is based on the standard VNC source and includes new
TightVNC-specific features and fixes, such as additional low-bandwidth
optimizations, major GUI improvements, and more.

There are three basic ways to use TigerVNC Java viewer:
  1. Running applet as part of TigerVNC server installation.
  2. Running applet hosted on a standalone Web server.
  3. Running the viewer as a standalone application.

%files java
%{_javadir}/*.jar
%{_datadir}/%{name}

#------------------------------------------------------------------------------

%prep
%setup -q -a2

%patch4 -p1 -b .cookie
%patch10 -p1 -b .ldnow
%patch11 -p1 -b .gethomedir
%patch13 -p1 -b .rh692048

cp -r /usr/share/x11-server-source/* unix/xserver
pushd unix/xserver
for all in `find . -type f -perm -001`; do
	chmod -x "$all"
done
patch -p1 -b --suffix .vnc < ../xserver113.patch
popd

%patch14 -p1 -b .glx

%build
# Temporary build with -fno-omit-frame-pointer, it causes problems
export CFLAGS="%{optflags} -fno-omit-frame-pointer"
export CXXFLAGS="$CFLAGS"

%{cmake}
%make
cd ..

# XXX: I'm not sure this define is actually needed
# Need this for shared objects that reference X Server, or other modules symbols
# Search for modules in extra_module_dir before the default path.
# This will allow fglrx to install its modified modules in more cleaner way.
%define extra_module_dir %{_libdir}/xorg/extra-modules

pushd unix/xserver
rm -f configure
autoreconf -fiv

# After the "--disable-config-hal", most options are just a paste from
# Mandriva's x11-server. We need to check what we can clean here (without
# reducing features)
%configure2_5x  --disable-xorg \
		--disable-xwin \
		--disable-xvfb \
		--disable-xnest \
		--disable-dmx \
		--disable-xfbdev \
		--disable-xephyr \
		--disable-kdrive \
		--disable-config-dbus \
		--disable-config-hal \
		--disable-static \
		--disable-unit-tests \
		--with-log-dir=%{_logdir} \
		--with-os-vendor="Rosa" \
		--with-os-name="`echo \`uname -s -r\` | sed -e s'/ /_/g'`" \
		--with-vendor-web="http://rosalinux.com" \
		--with-extra-module-dir=%{extra_module_dir} \
		--enable-xwrapper \
		--enable-pam \
		--with-default-font-path="catalogue:%{_sysconfdir}/X11/fontpath.d"

make
popd

# Build icons
pushd media
%make
popd

# Build java
pushd java
%{cmake}
cd ..
popd

%install
rm -rf %{buildroot}

push build
%makeinstall_std
popd

pushd unix/xserver/hw/vnc
%makeinstall_std
popd

# Install desktop stuff
mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/{16x16,24x24,48x48}/apps

pushd media/icons
    for s in 16 24 48; do
	install -m644 tigervnc_$s.png %{buildroot}/%{_datadir}/icons/hicolor/${s}x$s/apps/tigervnc.png
    done
popd

mkdir %{buildroot}/%{_datadir}/applications
desktop-file-install \
	--dir %{buildroot}%{_datadir}/applications \
	%{SOURCE1}

%find_lang %{name} %{name}.lang

# remove unwanted files
rm -f  %{buildroot}/%{_libdir}/xorg/modules/extensions/libvnc.la


# java
install -d -m 755 %{buildroot}%{_javadir}
install -d -m 755 %{buildroot}%{_datadir}/%{name}/classes
pushd java/src/com/tigervnc/vncviewer
    make install INSTALL_DIR=%{buildroot}%{_datadir}/%{name}/classes \
    ARCHIVE=vncviewer-%{version}.jar
popd

pushd %{buildroot}%{_datadir}/%{name}/classes
    mv vncviewer-%{version}.jar %{buildroot}%{_javadir}
    ln -s %{_javadir}/vncviewer-%{version}.jar VncViewer.jar
popd

pushd %{buildroot}%{_javadir}
    ln -s vncviewer-%{version}.jar vncviewer.jar
    ln -s vncviewer-%{version}.jar VncViewer.jar
popd

%changelog
* Thu Sep 01 2011 Guilherme Moro <guilherme@mandriva.com> 1.1.0-0mdv2012.0
+ Revision: 697750
- updated to version 1.1.0

* Tue Aug 30 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.0.90-0.201103164362.2
+ Revision: 697519
- fix linkage against forgotten local static library
- fix api change of local library

  + Oden Eriksson <oeriksson@mandriva.com>
    - new S3
    - try applying the x11 patch

* Thu Jun 02 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.90-0.201103164362.1
+ Revision: 682426
- fix build
- new 1.0.90 source, essentially this is 1.1beta1 and it's the official tar ball
- sync patches with tigervnc-1.0.90-5.fc16.src.rpm which also fixes CVE-2011-1775
- unify the xserver19 patch as S3

  + Paulo Ricardo Zanoni <pzanoni@mandriva.com>
    - Remove deprecated Encoding key from desktop file

* Thu Jan 13 2011 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201012034210.6
+ Revision: 631010
- Obsolete RealVNC packages

* Tue Dec 28 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201012034210.5mdv2011.0
+ Revision: 625668
- BR java-devel
- Add -java package
- Use %%makeinstall_std

* Thu Dec 23 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201012034210.4mdv2011.0
+ Revision: 624170
- Remove sysconfig, initscript and require vnc-server-common
- Fix dekstop file categories
- Update summaries, descriptions, profiles, conflicts and groups (part of vnc
  packages standardization)

* Thu Dec 16 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201012034210.3mdv2011.0
+ Revision: 622330
- Add patches to fix problems with scrollbars.

* Wed Dec 08 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201012034210.2mdv2011.0
+ Revision: 616320
- Add initscript file
- Add sysconfig/vncservers file
- Use configure2_5x
- Use system jpeg
- Remove unrecognized configure options
- Don't chmod files copied by x11-server-source

* Mon Dec 06 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201012034210.1mdv2011.0
+ Revision: 612395
- Update to newer revision
- Use xserver19 patch
- Fix linking

* Wed May 05 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201004234031.2mdv2010.1
+ Revision: 542633
- Remove sed in Makefile.am (was breaking libvnc.so)
- Add URL tag

* Fri Apr 23 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.0.90-0.201004234031.1mdv2010.1
+ Revision: 538366
- import tigervnc

