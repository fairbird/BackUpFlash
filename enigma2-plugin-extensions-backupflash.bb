DESCRIPTION = "BackUpFlash plugin by (RAED & mfaraj57) to Create Backup and flash. Also to download Some Team images."
MAINTAINER = "RAED - fairbird"
LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://LICENSE;md5=1ebbd3e34237af26da5dc08a4e440464"

SRC_URI = "git://github.com/fairbird/BackUpFlash;protocol=https;branch=main"

inherit gitpkgv distutils-openplugins

RDEPENDS_${PN} += "\
	wget \
	python-crypt \
	pigz \
	xz \
	pigz \
	flash-scripts \
	"

S = "${WORKDIR}/git"

SRCREV = "${AUTOREV}"

PV = "1.1+git${SRCPV}"
PKGV = "1.1+git${GITPKGV}"

FILES_${PN} = "${prefix}/"

do_install() {
	install -d ${D}${prefix}
	cp -r ${S}${prefix}/* ${D}${prefix}/
}

do_package_qa[noexec] = "1"

INSANE_SKIP_${PN} += "already-stripped"
